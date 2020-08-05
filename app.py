import streamlit as st
from streamlit.ReportThread import get_report_ctx
from streamlit.hashing import _CodeHasher
from streamlit.server.Server import Server
import pandas as pd
from newsapi import NewsApiClient
import json
import requests
import streamlit_theme as stt
import pickle
import hashlib

from summarizer import Summarizer

# DB
from managed_db import *

# Functions
from functions import *


def main():
    state = _get_state()
    stt.set_theme({'primary': '#1b3388'})
    state.newsapi = NewsApiClient(api_key='68353e14ce514929ac111b8b0f24556e')
    #state.model = Summarizer()
    pages = {
        "Login": page_login,
        "Home": page_home,
        "Signup": page_signup,
    }

    st.sidebar.title(":newspaper: SummarizeR")
    page = st.sidebar.radio("Select your page", tuple(pages.keys()))

    # Display the selected page with the session state
    pages[page](state)

    # Mandatory to avoid rollbacks with widgets, must be called at the end of your app
    state.sync()


def page_login(state):
    st.title(":newspaper: SummarizeR")
    st.title(":copyright: Login page")
    state.username = st.text_input("User Name")
    state.password = st.text_input("Password",type='password')
    if st.button("Login"):
        create_usertable()
        state.hashed_pswd = make_hashes(state.password)
        state.result = login_user(state.username,check_hashes(state.password,state.hashed_pswd))
        if state.result:
            st.success(":congratulations: Logged In as {}".format(state.username))
        else:
            st.warning(":registered: Incorrect Username/Password. Please check or SignUp")

def page_home(state):
    st.title(":newspaper: SummarizeR")
    if state.result:
        task = st.selectbox("Browse Menu",["Todays News","Search News", "News Summary", "Profile","User Preferences"])

        if task == "Profile":
            st.subheader("View Your Profile")
            display_preferences(state.username,state.password,state.hashed_pswd)
        elif task == "Todays News":
            df_news = call_api_news()
            df_disp_news = format_display_news(df_news)
            st.write(df_disp_news.to_html(escape = False), unsafe_allow_html = True)
        elif task == "Search News":
            st.subheader("Search Your News")
            search_type = st.radio("Go to", ['Search', 'User Profile'])
            if search_type == 'Search':
                search_query = st.text_input("Search")
                if search_query:
                    start_date, end_date = st.date_input("range, no dates", [])
                    if start_date:
                        df_search = search_news(search_type,state.newsapi,state.username,state.password,state.hashed_pswd,start_date,end_date,search_query)
                        df_disp_search = format_display_news(df_search)
                        st.write(df_disp_search.to_html(escape = False), unsafe_allow_html = True)
            else:
                user_pref = user_preference(state.username,check_hashes(state.password,state.hashed_pswd))
                if len(user_pref[0][0]) == 4:
                    return st.write("Please update the user preferences")
                else:
                    start_date, end_date = st.date_input("range, no dates", [])
                    if start_date:
                        df_search = search_news(search_type,state.newsapi,state.username,state.password,state.hashed_pswd,start_date,end_date,search_query='')
                        df_disp_search = format_display_news(df_search)
                        st.write(df_disp_search.to_html(escape = False), unsafe_allow_html = True)
        elif task == "News Summary":
            #model = Summarizer()
            options = ["Select Article", "Inset Article"]
            article = st.radio("Pick One", options)
            clean_article_flag = "Flase"
            if article == "Select Article":
                uploaded_file = st.selectbox("Select Article",["Select Article", "Apple","Entertainment","Facebook","Music","Sports","Stocks"])
                if uploaded_file == "Apple":
                    raw_article, clean_article = read_article('Apple_News.txt')
                    clean_article_flag = "True"
                elif uploaded_file == "Entertainment":
                    raw_article, clean_article = read_article('Entertainment.txt')
                    clean_article_flag = "True"
                elif uploaded_file == "Facebook":
                    raw_article, clean_article = read_article('Facebook.txt')
                    clean_article_flag = "True"
                elif uploaded_file == "Music":
                    raw_article, clean_article = read_article('Music.txt')
                    clean_article_flag = "True"
                elif uploaded_file == "Sports":
                    raw_article, clean_article = read_article('Sports.txt')
                    clean_article_flag = "True"
                elif uploaded_file == "Stocks":
                    raw_article, clean_article = read_article('Stocks.txt')
                    clean_article_flag = "True"
                elif uploaded_file == "Select Article":
                    st.write("Please select article from the dropdown")

            elif article == "Inset Article":
                article = st.text_area('Input your article here:')
                raw_article, clean_article = read_article('',article)
                clean_article_flag = "True"

            if clean_article_flag == "True":
                st.write(raw_article)
                if st.button("Summarize"):
                    model = Summarizer()
                    result = model(clean_article)
                    summary = ''.join(result)
                    st.write(summary)
                    # st.write("Please wait for the model results")

        elif task == "Profile":
            display_preferences(state.username,state.password,state.hashed_pswd)

        elif task == 'User Preferences':
            st.subheader("User Preferences")
            df = call_api_source()
            df1 = df[['id', 'name', 'category']]
            df1.rename(columns={'id':'Unique_Id', 'name':'Site_Name', 'category':'News_Category'}, inplace=True)
            st.dataframe(df1.style)
            sites = st.multiselect("Choose Prefered Site", df1["Site_Name"].unique())
            pick_all_sites = st.checkbox(' or all news sites')
            category = st.multiselect("Choose Prefered Category", df1["News_Category"].unique())
            pick_all_category = st.checkbox(' or all category')
            sites_selected = False
            if not pick_all_sites:
                if sites:
                    selected_sites = pd.DataFrame(df1[df1['Site_Name'].isin(sites)])
                    sites_selected = True
            else:
                selected_sites = pd.DataFrame(df1['Site_Name'].unique())
                sites_selected = True
            category_selected = False
            if not pick_all_category:
                if category:
                    selected_category = pd.DataFrame(df1[df1['News_Category'].isin(category)])
                    category_selected = True
            else:
                selected_category = pd.DataFrame(df1['News_Category'].unique())
                category_selected = True

            if 	sites_selected == True & category_selected == True:
                selection = st.radio("Go to", ['All Combinations', 'Specified Combinations'])
                if selection == 'All Combinations':
                    result = df1[(df1.Site_Name.isin(selected_sites.Site_Name)) | (df1.News_Category.isin(selected_category.News_Category))]
                else:
                    result = df1[(df1.Site_Name.isin(selected_sites.Site_Name)) & (df1.News_Category.isin(selected_category.News_Category))]

                if st.button("Set Preferences"):
                    preferences = result.to_json(orient="columns")
                    update_user_preference(state.username, check_hashes(state.password,state.hashed_pswd), preferences)
                    display_preferences(state.username,state.password,state.hashed_pswd)
                    st.write("Prefered News avilable in **Todays News** ")
    else:
        st.warning(":registered: Incorrect Username/Password. Please check or SignUp")

def page_signup(state):
    st.title(":newspaper: SummarizeR")
    st.subheader("Create New Account")
    state.new_user = st.text_input("Username")
    state.new_email = st.text_input("Email")
    state.new_password = st.text_input("Password",type='password')
    if st.button("Signup"):
        create_usertable()
        add_userdata(state.new_user,make_hashes(state.new_password), state.new_email, 'NULL')
        st.success(":congratulations: You have successfully created a valid Account")
        st.info("**Login to personalize the news articles**")

def page_state(state):
    st.title(":wrench: Settings")
    display_state_values(state)

    st.write("---")
    options = ["Hello", "World", "Goodbye"]
    state.input = st.text_input("Set input value.", state.input or "")
    state.slider = st.slider("Set slider value.", 1, 10, state.slider)
    state.radio = st.radio("Set radio value.", options, options.index(state.radio) if state.radio else 0)
    state.checkbox = st.checkbox("Set checkbox value.", state.checkbox)
    state.selectbox = st.selectbox("Select value.", options, options.index(state.selectbox) if state.selectbox else 0)
    state.multiselect = st.multiselect("Select value(s).", options, state.multiselect)

    # Dynamic state assignments
    for i in range(3):
        key = f"State value {i}"
        state[key] = st.slider(f"Set value {i}", 1, 10, state[key])


def display_state_values(state):
    st.write("Input state:", state.input)
    st.write("Slider state:", state.slider)
    st.write("Radio state:", state.radio)
    st.write("Checkbox state:", state.checkbox)
    st.write("Selectbox state:", state.selectbox)
    st.write("Multiselect state:", state.multiselect)

    for i in range(3):
        st.write(f"Value {i}:", state[f"State value {i}"])

    if st.button("Clear state"):
        state.clear()


class _SessionState:

    def __init__(self, session, hash_funcs):
        """Initialize SessionState instance."""
        self.__dict__["_state"] = {
            "data": {},
            "hash": None,
            "hasher": _CodeHasher(hash_funcs),
            "is_rerun": False,
            "session": session,
        }

    def __call__(self, **kwargs):
        """Initialize state data once."""
        for item, value in kwargs.items():
            if item not in self._state["data"]:
                self._state["data"][item] = value

    def __getitem__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __getattr__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __setitem__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def __setattr__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def clear(self):
        """Clear session state and request a rerun."""
        self._state["data"].clear()
        self._state["session"].request_rerun()

    def sync(self):
        """Rerun the app with all state values up to date from the beginning to fix rollbacks."""

        # Ensure to rerun only once to avoid infinite loops
        # caused by a constantly changing state value at each run.
        #
        # Example: state.value += 1
        if self._state["is_rerun"]:
            self._state["is_rerun"] = False

        elif self._state["hash"] is not None:
            if self._state["hash"] != self._state["hasher"].to_bytes(self._state["data"], None):
                self._state["is_rerun"] = True
                self._state["session"].request_rerun()

        # self._state["hash"] = self._state["hasher"].to_bytes(self._state["data"], None)


def _get_session():
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")

    return session_info.session


def _get_state(hash_funcs=None):
    session = _get_session()

    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = _SessionState(session, hash_funcs)

    return session._custom_session_state


if __name__ == "__main__":
    main()
