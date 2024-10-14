import streamlit as st
import pymongo


@st.cache_resource
def init_connection():
    client = pymongo.MongoClient(st.secrets["mongo"]["url"])
    db = client["nnkhuongduy"]

    return db


db = init_connection()


@st.cache_data(ttl=600)
def get_episodes():
    episode_collection = db["trash_taste"]
    episodes = list(episode_collection.find({}, sort={"date": 1}))

    return episodes


def get_watching_episode():
    var_collection = db["variables"]
    watching_episode = var_collection.find_one({"name": "watching_index"})

    if watching_episode is None:
        var_collection.insert_one({"name": "watching_index", "value": 0})
        watching_episode = var_collection.find_one({"name": "watching_index"})

    if watching_episode is None:
        raise Exception()

    return dict(watching_episode)


def get_index():
    watching_episode = get_watching_episode()
    watching_index = watching_episode.get("value")

    if not isinstance(watching_index, int):
        raise Exception("")

    return watching_index


episodes = get_episodes()

if "index" not in st.session_state:
    st.session_state.index = get_index()

st.title("Trash taste binging!")

if st.button(
    "Previous episode", disabled=st.session_state.index == 0, use_container_width=True
):
    var_collection = db["variables"]
    var_collection.find_one_and_update(
        {"name": "watching_index"},
        {"$set": {"value": max(st.session_state.index - 1, 0)}},
    )
    st.session_state.index = get_index()
    st.rerun()

st.write(episodes[st.session_state.index].get("title"))
st.link_button(
    "Open Youtube",
    episodes[st.session_state.index].get("url"),
    icon=":material/open_in_new:",
)


if st.button(
    "Next episode",
    disabled=st.session_state.index == len(episodes) - 1,
    use_container_width=True,
):
    var_collection = db["variables"]
    var_collection.find_one_and_update(
        {"name": "watching_index"},
        {"$set": {"value": min(st.session_state.index + 1, len(episodes) - 1)}},
    )
    st.write(st.session_state.index + 1)
    st.session_state.index = get_index()
    st.rerun()


if "selecting" not in st.session_state:
    st.session_state.selecting = False

if st.button("Select episode", use_container_width=True):
    st.session_state.selecting = not st.session_state.selecting


if st.session_state.selecting:
    option = st.selectbox(
        "Episode:", (episode.get("title") for episode in episodes), index=None
    )

    if option:
        index = next((i for i, d in enumerate(episodes) if d["title"] == option))

        var_collection = db["variables"]
        var_collection.find_one_and_update(
            {"name": "watching_index"},
            {"$set": {"value": index}},
        )

        st.session_state.index = index
        st.session_state.selecting = False
        st.rerun()
