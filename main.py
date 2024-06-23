import streamlit as st
import requests
import urllib.parse
import json



# Cấu hình Threads API
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

REDIRECT_URI = "https://threads-api-nguyenngothuong-v1.streamlit.app/"  # Streamlit mặc định chạy trên cổng 8501

# Hàm để lấy access token
def get_access_token(code):
    token_url = "https://graph.threads.net/oauth/access_token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    response = requests.post(token_url, data=data)
    return response.json().get("access_token")

# Hàm để lấy thông tin người dùng
def get_user_info(access_token):
    user_url = "https://graph.threads.net/v1.0/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(user_url, headers=headers)
    return response.json()

# Hàm để đăng bài lên Threads
def post_to_threads(access_token, user_id, message):
    post_url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "text": message
    }
    response = requests.post(post_url, headers=headers, data=data)
    return response.json()

# Tạo URL xác thực
auth_url = f"https://threads.net/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&scope=threads_basic,threads_content_publish&response_type=code"

# Giao diện Streamlit
st.title("Threads API Integration")

if "access_token" not in st.session_state:
    st.session_state.access_token = None
    st.session_state.user_info = None

if st.session_state.access_token is None:
    st.markdown(f"[Authenticate with Threads]({auth_url})")
    code = st.text_input("Enter the code from the redirect URL:")
    if code:
        access_token = get_access_token(code)
        if access_token:
            st.session_state.access_token = access_token
            st.success("Authentication successful!")
            st.session_state.user_info = get_user_info(access_token)
        else:
            st.error("Failed to get access token. Please try again.")
else:
    st.success("You are authenticated!")
    
    if st.session_state.user_info:
        st.write(f"Welcome, {st.session_state.user_info.get('username', 'User')}!")
        
        # Hiển thị thông tin người dùng
        if st.checkbox("Show user info"):
            st.json(st.session_state.user_info)
        
        # Đăng bài lên Threads
        message = st.text_area("Enter your message to post on Threads:")
        if st.button("Post to Threads"):
            if message:
                result = post_to_threads(st.session_state.access_token, st.session_state.user_info['id'], message)
                if 'id' in result:
                    st.success(f"Posted successfully! Post ID: {result['id']}")
                else:
                    st.error(f"Failed to post. Error: {json.dumps(result)}")
            else:
                st.warning("Please enter a message to post.")

    if st.button("Logout"):
        st.session_state.access_token = None
        st.session_state.user_info = None
        st.experimental_rerun()