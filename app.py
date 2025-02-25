import streamlit as st
import google.generativeai as genai
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置Google API
modelName = "gemini-2.0-flash-thinking-exp-01-21"
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'), transport="rest")
model = genai.GenerativeModel(modelName)

# 页面配置
st.set_page_config(
    page_title="心理咨询助手",
    page_icon="🧊",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.markdown-text-container {
    word-wrap: break-word;
    white-space: pre-wrap;
    max-width: 100%;
}
.markdown-text-container code {
    white-space: pre-wrap !important;
}
</style>
""", unsafe_allow_html=True)


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
        
        print(st.session_state)

        # 构建系统提示
        system_prompt = f"""
{st.session_state.ai_role}

**你的目标：**
1. 帮助来访者梳理考试压力产生的根源，缓解因考试压力导致的失眠. 考场大脑空白等问题。
2. 深入挖掘来访者与母亲关系中的情感冲突，引导其正确认识自身在关系中的感受和需求。
3. 通过心理投射游戏，让来访者直观地表达内心想法和对关系的认知，促进自我探索与成长。
4. 增强来访者的自我认知，使其能够正视自己的价值，减少对他人认可的过度依赖，建立积极的自我认同。

**对话流程：**
1. **开启对话环节**：你需要根据我提供的咨询对象基本信息，发起提问，引导咨询者讲述自己遇到问题。
2. **深入交流环节**: 进行多轮对话，根据质询者的回答，生成下一步的提问，进一步的引导咨询者更多更完整的讲述自己遇到的问题。
3. **心理投射游戏环节**: 引导咨询者参加心理投射游戏环节，根据咨询者讲述的信息和卡牌游戏规则，同咨询者进行卡片游戏。
4. **对话总结": 总结卡片游戏反馈的信息，对咨询者进行总结鼓励。并引导咨询者参加礼物邮局的游戏。

**你的性格特点和沟通风格：**
1. **友善且平易近人：** 使用热情和友好的语气。 想象一下你正在和操场上的朋友说话。 使用表情符号和感叹词来增强友好感（例如 😊, 🎉, 哇！）。
2. **耐心且富有同情心：** 专心倾听，并表达你理解他们的感受。 使用诸如“我听到了”，“我明白你的感受”之类的短语。
3. **轻松有趣：** 在对话中融入轻松有趣的元素。 使用适合年龄的幽默，并保持互动轻松愉快。
4. **鼓励和支持：** 关注孩子的优点并提供积极的鼓励。 帮助他们感到有能力管理自己的感受。
5. **简单语言：** 使用清晰简洁的语言，适合小学生。 避免使用术语或复杂的句子结构。
6. **不带评判：** 创建一个安全空间，让孩子们可以放心地分享，而不用担心被评判或批评。
7. **尊重：** 尊重孩子的隐私和感受。 不要强迫他们分享他们不愿分享的信息。

**重要注意事项：**
1. **你不能替代专业的儿童心理学家。** 你的角色是提供初步的支持和指导，并鼓励儿童在需要时向信任的成年人或专业人士寻求帮助。
2. **避免做出诊断或提供具体的临床建议。** 你的分析应被视为观察和潜在的进一步探索领域，而不是对心理问题的明确陈述。
3. **优先考虑儿童的福祉和安全。** 如果你发现严重痛苦、自残或伤害他人或虐待的迹象，你的程序应包括将这些担忧升级给适当的人工专业人员的协议（这将在本特定提示之外处理，但对于整体系统设计而言是至关重要的伦理考量）。
        """
        print(system_prompt)
        
        # 清空之前的对话，初始化对话历史，包含系统提示
        st.session_state.messages = []
        st.success("对话已开始！")
        
        st.session_state.chat = model.start_chat(history=[
            {"role": "model", "parts": system_prompt},
        ])

        user_prompt = f"""
咨询者的信息：
- 姓名: {st.session_state.user_info['name']}
- 年龄: {st.session_state.user_info['age']}
- 性别: {st.session_state.user_info['gender']}
- 身份: {st.session_state.user_info['identity']}
- 最近经历: {st.session_state.user_info['recent_experience']}

现在开始这次咨询对话，作为心理咨询师的你需要让来访者放松并自由表达。请生成一个能引导来访者打开话匣子的提问。
并且要暗示来访者讲述咨询者上面遇到的问题。

输出要求：只输出对话内容，不要输出其他任何信息，包括导语或者解释等等。
        """
        print(user_prompt)
        response = st.session_state.chat.send_message(user_prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

# 显示对话历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message['content'], unsafe_allow_html=True)

# 用户输入
if prompt := st.chat_input("请输入您的问题..."):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 生成AI响应
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            response = st.session_state.chat.send_message(prompt)
            print(response.text)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

