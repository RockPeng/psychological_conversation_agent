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
        "name": "小朵",  # 设置姓名默认值为小朵
        "age": None,
        "gender": None,
        "identity": "小学生",  # 增加身份字段，默认值为小学生
        "recent_experience": "正面对小升初的考试压力，出现失眠、考场发挥不佳等问题，内心受父母期待影响，存在与母亲关系方面的困扰，前来寻求心理咨询帮助。",  # 设置默认经历
    }

if "ai_role" not in st.session_state:
    st.session_state.ai_role = "你是一位AI心理咨询师, 名字叫：心语老师。\n具备丰富心理学经验，运用游戏疗愈和心理投射游戏开展心理咨询工作，通过引导对话、提问和互动，帮助来访者探索内心世界、解决心理困扰。"

# 侧边栏配置
with st.sidebar:
    st.title("心理咨询对话")  
    st.divider()
    # AI角色配置
    ai_role = st.text_area(
        "请输入AI角色设定",
        value=st.session_state.ai_role,
        height=120
    )
    
    st.divider()
    
    # 用户信息配置
    st.subheader("用户信息")
    name = st.text_input("姓名", value=st.session_state.user_info["name"])
    age = st.number_input("年龄", min_value=0, max_value=120, value=st.session_state.user_info["age"] or 12)
    gender = st.radio("性别", ["男", "女"], index=1 if st.session_state.user_info["gender"] is None else ["男", "女"].index(st.session_state.user_info["gender"]))
    identity = st.text_input("身份", value=st.session_state.user_info["identity"])  # 增加身份输入框
    recent_experience = st.text_area(
        "最近的经历",
        value=st.session_state.user_info["recent_experience"],
        height=96
    )
    
    # 保存用户信息
    if st.button("开始对话", use_container_width=True, type="primary"):
        st.session_state.user_info = {
            "name": name,
            "age": age,
            "gender": gender,
            "identity": identity,
            "recent_experience": recent_experience
        }
        st.session_state.ai_role = ai_role
        
        # 构建系统提示
        system_prompt = f"""
        用户信息:
        - 姓名: {st.session_state.user_info['name']}
        - 年龄: {st.session_state.user_info['age']}
        - 性别: {st.session_state.user_info['gender']}
        - 身份: {st.session_state.user_info['identity']}
        - 最近经历: {st.session_state.user_info['recent_experience']}

        AI角色设定:
        {st.session_state.ai_role}
        """
        
        # 清空之前的对话，初始化对话历史，包含系统提示
        st.session_state.messages = [{"role": "system", "content": system_prompt}]
        st.success("对话已开始！")
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
    - 身份: {st.session_state.user_info['identity']}
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

