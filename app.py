import streamlit as st
import google.generativeai as genai
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置Google API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# 页面配置
st.set_page_config(
    page_title="心理咨询助手",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "name": "",
        "age": None,
        "gender": None,
        "recent_experience": "",
    }

if "ai_role" not in st.session_state:
    st.session_state.ai_role = ""

# 侧边栏配置
with st.sidebar:
    st.title("心理咨询对话")  
    st.divider()
    # AI角色配置
    ai_role = st.text_area(
        "请输入AI角色设定",
        value=st.session_state.ai_role,
        height=150
    )
    
    st.divider()
    
    # 用户信息配置
    st.subheader("用户信息")
    name = st.text_input("姓名", value=st.session_state.user_info["name"])
    age = st.number_input("年龄", min_value=0, max_value=120, value=st.session_state.user_info["age"] or 12)
    gender = st.radio("性别", ["男", "女"], index=1 if st.session_state.user_info["gender"] is None else ["男", "女", "其他"].index(st.session_state.user_info["gender"]))
    recent_experience = st.text_area(
        "最近的经历",
        value=st.session_state.user_info["recent_experience"],
        height=150
    )
    
    # 保存用户信息
    if st.button("保存信息"):
        st.session_state.user_info = {
            "name": name,
            "age": age,
            "gender": gender,
            "recent_experience": recent_experience
        }
        st.session_state.ai_role = ai_role
        st.success("信息已保存！")

# 添加"开始对话"按钮
if st.button("开始对话"):
    # 构建系统提示
    system_prompt = f"""
    用户信息:
    - 姓名: {st.session_state.user_info['name']}
    - 年龄: {st.session_state.user_info['age']}
    - 性别: {st.session_state.user_info['gender']}
    - 最近经历: {st.session_state.user_info['recent_experience']}

    AI角色设定:
    {st.session_state.ai_role}
    """
    # 初始化对话历史，包含系统提示
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.experimental_rerun() # 强制页面刷新

# 显示对话历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("请输入您的问题..."):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 构建完整的上下文
    context = f"""
    用户信息:
    - 姓名: {st.session_state.user_info['name']}
    - 年龄: {st.session_state.user_info['age']}
    - 性别: {st.session_state.user_info['gender']}
    - 最近经历: {st.session_state.user_info['recent_experience']}
    
    AI角色设定:
    {st.session_state.ai_role}
    """
    
    # 生成AI响应
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            chat = model.start_chat(history=[])
            response = chat.send_message(context + "\n\n" + prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

