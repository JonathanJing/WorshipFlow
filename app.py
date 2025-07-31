import streamlit as st
import os
from datetime import datetime
from config import Config
from logger import user_logger

st.set_page_config(
    page_title="灵泉Flow (WorshipFlow)",
    page_icon="🎵",
    layout="wide"
)

@st.cache_resource
def get_config():
    try:
        return Config()
    except Exception as e:
        st.error(f"配置错误: {e}")
        st.stop()

config = get_config()

def song_manager_page():
    """
    Song Library Management Page / 诗歌库管理页面
    
    This function renders the song management interface with two tabs:
    1. Add new songs with metadata and lyrics
    2. Browse and search existing songs
    
    该函数渲染诗歌管理界面，包含两个标签页：
    1. 添加新诗歌及其元数据和歌词
    2. 浏览和搜索现有诗歌
    """
    st.header("🎵 诗歌库管理")  # Song Library Management
    
    tab1, tab2 = st.tabs(["添加新歌", "查看诗歌"])  # Add New Song, View Songs
    
    with tab1:
        st.subheader("添加新诗歌")  # Add New Song
        
        with st.form("add_song_form"):
            title = st.text_input("诗歌标题 *", placeholder="例如: Here I Am to Worship")
            author = st.text_input("作者", placeholder="例如: Tim Hughes")
            key = st.text_input("调性", placeholder="例如: D")
            lyrics = st.text_area("歌词 *", height=200, placeholder="请输入完整歌词...")
            
            st.write("标签:")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                tag_praise = st.checkbox("赞美")
                tag_worship = st.checkbox("敬拜")
            with col2:
                tag_quiet = st.checkbox("安静")
                tag_celebration = st.checkbox("庆祝")
            with col3:
                tag_prayer = st.checkbox("祷告")
                tag_response = st.checkbox("回应")
            with col4:
                tag_communion = st.checkbox("圣餐")
                tag_christmas = st.checkbox("圣诞")
            
            custom_tags = st.text_input("自定义标签", placeholder="用逗号分隔多个标签")
            
            submitted = st.form_submit_button("保存诗歌")
            
            if submitted:
                if not title or not lyrics:
                    st.error("请填写诗歌标题和歌词")
                else:
                    tags = []
                    if tag_praise: tags.append("赞美")
                    if tag_worship: tags.append("敬拜")
                    if tag_quiet: tags.append("安静")
                    if tag_celebration: tags.append("庆祝")
                    if tag_prayer: tags.append("祷告")
                    if tag_response: tags.append("回应")
                    if tag_communion: tags.append("圣餐")
                    if tag_christmas: tags.append("圣诞")
                    
                    if custom_tags:
                        custom_tag_list = [tag.strip() for tag in custom_tags.split(',')]
                        tags.extend(custom_tag_list)
                    
                    song_id = title.lower().replace(' ', '_').replace('(', '').replace(')', '')
                    song_data = {
                        "title": title,
                        "author": author,
                        "key": key,
                        "lyrics": lyrics,
                        "tags": tags
                    }
                    
                    try:
                        config.save_song(song_id, song_data)
                        
                        # Log successful song addition
                        user_logger.log_song_action("song_added", song_data)
                        
                        # 显示详细的成功信息
                        success_msg = f"✅ **诗歌添加成功！**\n\n"
                        success_msg += f"**标题:** {title}\n"
                        if author:
                            success_msg += f"**作者:** {author}\n"
                        if key:
                            success_msg += f"**调性:** {key}\n"
                        if tags:
                            success_msg += f"**标签:** {', '.join(tags)}\n"
                        success_msg += f"**保存位置:** data/songs/{song_id}.json"
                        
                        st.success(success_msg)
                        
                        # 显示后续操作提示
                        st.info("💡 **接下来你可以:**\n- 在「查看诗歌」标签页中查看刚添加的诗歌\n- 前往「敬拜流程设计」页面使用这首诗歌")
                        
                        # 自动刷新页面以清空表单
                        st.rerun()
                    except Exception as e:
                        # Log error
                        user_logger.log_error("song_save_failed", str(e), {"song_title": title})
                        st.error(f"❌ 保存失败: {e}")
    
    with tab2:
        st.subheader("诗歌库")
        
        songs = config.load_songs()
        
        if not songs:
            st.info("诗歌库为空，请先添加一些诗歌。")
            return
        
        search_term = st.text_input("搜索诗歌", placeholder="按标题、作者或标签搜索...")
        
        filtered_songs = songs
        if search_term:
            filtered_songs = {
                k: v for k, v in songs.items() 
                if search_term.lower() in v.get('title', '').lower() 
                or search_term.lower() in v.get('author', '').lower()
                or any(search_term.lower() in tag.lower() for tag in v.get('tags', []))
            }
        
        if filtered_songs:
            song_titles = [v['title'] for v in filtered_songs.values()]
            selected_title = st.selectbox("选择诗歌", song_titles)
            
            if selected_title:
                selected_song = next(v for v in filtered_songs.values() if v['title'] == selected_title)
                
                # Log song view
                user_logger.log_song_action("song_viewed", selected_song)
                
                st.write("---")
                st.write(f"**标题:** {selected_song['title']}")
                if selected_song.get('author'):
                    st.write(f"**作者:** {selected_song['author']}")
                if selected_song.get('key'):
                    st.write(f"**调性:** {selected_song['key']}")
                if selected_song.get('tags'):
                    st.write(f"**标签:** {', '.join(selected_song['tags'])}")
                
                st.write("**歌词:**")
                st.text(selected_song['lyrics'])
        else:
            st.info("没有找到匹配的诗歌。")

def worship_flow_designer():
    """
    Worship Flow Designer Page / 敬拜流程设计器页面
    
    This function creates the main worship planning interface where users can:
    1. Input sermon information (title, scripture, date)
    2. Select worship songs in order
    3. Generate AI-powered transitions between songs
    4. Preview and save the complete worship flow
    
    该函数创建主要的敬拜规划界面，用户可以：
    1. 输入证道信息（标题、经文、日期）
    2. 按顺序选择敬拜诗歌
    3. 生成AI驱动的诗歌间过渡词
    4. 预览和保存完整的敬拜流程
    """
    st.header("✨ 敬拜流程设计器")  # Worship Flow Designer
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("主日信息")  # Sunday Service Information
        sermon_title = st.text_input("证道主题", placeholder="例如: 行在光明中", value="你曾怀疑过主吗")  # Sermon Topic
        key_scripture = st.text_input("核心经文", placeholder="例如: 约翰一书 1:7", value="马太福音 11:1-19")  # Key Scripture
        service_date = st.date_input("主日日期", datetime.now())  # Service Date
    
    with col2:
        st.subheader("选择诗歌")
        songs = config.load_songs()
        
        if not songs:
            st.warning("请先在诗歌库中添加一些诗歌。")
            return
        
        song_options = [(k, v['title']) for k, v in songs.items()]
        selected_songs = st.multiselect(
            "选择敬拜诗歌 (按顺序)",
            options=[k for k, _ in song_options],
            format_func=lambda x: next(title for k, title in song_options if k == x)
        )
    
    # 始终准备基础流程数据
    basic_flow_data = {
        "date": str(service_date),
        "sermon_title": sermon_title,
        "key_scripture": key_scripture,
        "worship_flow": []
    }
    
    if sermon_title and key_scripture and selected_songs:
        st.write("---")
        st.subheader("🎼 敬拜流程预览")
        
        if 'flow_data' not in st.session_state:
            st.session_state.flow_data = basic_flow_data
        
        for i, song_id in enumerate(selected_songs):
            song = songs[song_id]
            
            # Show transition section before each song
            if i == 0:
                # Opening transition for first song
                st.write(f"#### 🎬 敬拜开场引入《{song['title']}》")
                
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button(f"生成开场词", key=f"generate_opening_{i}"):
                        with st.spinner("正在生成开场词..."):
                            try:
                                transitions = generate_opening_transition(
                                    sermon_title, key_scripture, song
                                )
                                st.session_state[f"transition_{i}"] = transitions
                                
                                # Log successful AI generation
                                user_logger.log_ai_action(
                                    action="opening_transition_generated",
                                    model_name=config.get_current_model_name(),
                                    prompt_type="opening_transition",
                                    success=True,
                                    details={
                                        "sermon_title": sermon_title,
                                        "song_title": song['title'],
                                        "dimensions_generated": list(transitions.keys())
                                    }
                                )
                                
                                st.rerun()
                            except Exception as e:
                                # Log AI generation failure
                                user_logger.log_ai_action(
                                    action="opening_transition_failed",
                                    model_name=config.get_current_model_name(),
                                    prompt_type="opening_transition",
                                    success=False,
                                    details={
                                        "error": str(e),
                                        "sermon_title": sermon_title,
                                        "song_title": song['title']
                                    }
                                )
                                st.error(f"生成开场词失败: {e}")
                
                with col1:
                    if f"transition_{i}" in st.session_state:
                        st.write("**生成的开场词:**")
                        for dimension, content in st.session_state[f"transition_{i}"].items():
                            with st.expander(f"📝 {dimension}"):
                                st.write(content)
                                if st.button(f"使用此开场词", key=f"use_{i}_{dimension}"):
                                    st.session_state[f"selected_transition_{i}"] = content
                                    st.session_state[f"selected_dimension_{i}"] = dimension
                                    st.success(f"已选择「{dimension}」开场词!")
                                    st.rerun()
                        
                        # Show selected transition
                        if f"selected_transition_{i}" in st.session_state:
                            selected_dim = st.session_state.get(f"selected_dimension_{i}", "已选择")
                            st.success(f"✅ 已选择开场词 [{selected_dim}]: {st.session_state[f'selected_transition_{i}'][:50]}...")
                    else:
                        st.info("点击「生成开场词」按钮来为敬拜开始生成引导词")
                
                st.write("---")
                
            elif i > 0:
                # Regular transition between songs
                st.write(f"#### 🔗 从《{songs[selected_songs[i-1]]['title']}》到《{song['title']}》的串词")
                
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button(f"生成串词", key=f"generate_{i}"):
                        with st.spinner("正在生成串词..."):
                            try:
                                prev_song = songs[selected_songs[i-1]]
                                current_song = song
                                
                                transitions = generate_transitions(
                                    sermon_title, key_scripture, prev_song, current_song
                                )
                                st.session_state[f"transition_{i}"] = transitions
                                
                                # Log successful AI generation
                                user_logger.log_ai_action(
                                    action="transition_generated",
                                    model_name=config.get_current_model_name(),
                                    prompt_type="song_transition",
                                    success=True,
                                    details={
                                        "sermon_title": sermon_title,
                                        "from_song": prev_song['title'],
                                        "to_song": current_song['title'],
                                        "dimensions_generated": list(transitions.keys())
                                    }
                                )
                                
                                st.rerun()
                            except Exception as e:
                                # Log AI generation failure
                                user_logger.log_ai_action(
                                    action="transition_failed",
                                    model_name=config.get_current_model_name(),
                                    prompt_type="song_transition",
                                    success=False,
                                    details={
                                        "error": str(e),
                                        "sermon_title": sermon_title,
                                        "from_song": prev_song['title'] if 'prev_song' in locals() else "unknown",
                                        "to_song": current_song['title'] if 'current_song' in locals() else "unknown"
                                    }
                                )
                                st.error(f"生成串词失败: {e}")
                
                with col1:
                    if f"transition_{i}" in st.session_state:
                        st.write("**生成的串词:**")
                        for dimension, content in st.session_state[f"transition_{i}"].items():
                            with st.expander(f"📝 {dimension}"):
                                st.write(content)
                                if st.button(f"使用此串词", key=f"use_{i}_{dimension}"):
                                    st.session_state[f"selected_transition_{i}"] = content
                                    st.session_state[f"selected_dimension_{i}"] = dimension
                                    st.success(f"已选择「{dimension}」串词!")
                                    st.rerun()
                        
                        # Show selected transition
                        if f"selected_transition_{i}" in st.session_state:
                            selected_dim = st.session_state.get(f"selected_dimension_{i}", "已选择")
                            st.success(f"✅ 已选择串词 [{selected_dim}]: {st.session_state[f'selected_transition_{i}'][:50]}...")
                    else:
                        st.info("点击「生成串词」按钮来为这两首歌生成连接串词")
                
                st.write("---")
            
            # Show song details
            st.write(f"### {i+1}. 🎵 {song['title']}")
            
            with st.expander(f"查看 '{song['title']}' 详情"):
                st.write(f"**作者:** {song.get('author', '未知')}")
                st.write(f"**调性:** {song.get('key', '未指定')}")
                if song.get('tags'):
                    st.write(f"**标签:** {', '.join(song.get('tags', []))}")
                st.write("**歌词:**")
                st.text(song['lyrics'])
        
        st.write("---")
        
        # 准备流程数据
        flow_items = []
        for i, song_id in enumerate(selected_songs):
            # Add opening transition for first song or regular transitions for others
            if f"selected_transition_{i}" in st.session_state:
                dimension = st.session_state.get(f"selected_dimension_{i}", "未指定")
                transition_type = "opening" if i == 0 else "transition"
                
                flow_items.append({
                    "type": "transition_text",
                    "content": st.session_state[f"selected_transition_{i}"],
                    "dimension": dimension,
                    "transition_type": transition_type,
                    "from_song": selected_songs[i-1] if i > 0 else None,
                    "to_song": song_id
                })
            
            flow_items.append({
                "type": "song",
                "song_id": song_id
            })
        
        flow_data = {
            "date": str(service_date),
            "sermon_title": sermon_title,
            "key_scripture": key_scripture,
            "worship_flow": flow_items
        }
        
        # 将流程数据存储到session state中，以便排练模式使用
        st.session_state.rehearsal_flow = flow_data
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 保存敬拜流程", use_container_width=True):
                timestamp = datetime.now().strftime("%H%M%S")
                flow_id = f"{service_date}_{timestamp}_service"
                
                try:
                    config.save_flow(flow_id, flow_data)
                    
                    # Log successful flow save
                    user_logger.log_flow_action("flow_saved", flow_data)
                    
                    st.success("敬拜流程已保存!")
                    st.rerun()
                except Exception as e:
                    # Log error
                    user_logger.log_error("flow_save_failed", str(e), {
                        "sermon_title": sermon_title,
                        "flow_id": flow_id
                    })
                    st.error(f"保存失败: {e}")
        
        with col2:
            if st.button("🎭 进入排练模式", use_container_width=True):
                st.session_state.page = "rehearsal"
                st.rerun()
    
    else:
        # 即使没有完成所有步骤，也存储基础数据并提供排练模式入口
        st.session_state.rehearsal_flow = basic_flow_data
        
        st.write("---")
        st.info("💡 **提示:** 填写证道主题、核心经文并选择诗歌后，可以查看完整的敬拜流程预览")
        
        if st.button("🎭 进入排练模式", help="即使流程未完成也可以预览"):
            st.session_state.page = "rehearsal"
            st.rerun()

def generate_transitions(sermon_title, key_scripture, prev_song, current_song):
    """
    Generate AI-powered transitions between worship songs
    生成AI驱动的敬拜诗歌过渡词
    
    This function uses Gemini AI to create contextual transitions that bridge
    two worship songs, considering the sermon topic, scripture, and song lyrics.
    
    该函数使用Gemini AI创建上下文相关的过渡词，连接两首敬拜诗歌，
    考虑证道主题、经文和歌词内容。
    
    Args:
        sermon_title: The sermon topic / 证道主题
        key_scripture: The key scripture reference / 核心经文引用
        prev_song: Previous song data / 上一首歌数据
        current_song: Current song data / 当前歌曲数据
        
    Returns:
        Dict: Generated transitions in different dimensions / 不同维度的生成过渡词
    """
    model = config.get_model()
    
    prompt = f"""你是一位经验丰富的、属灵的基督徒敬拜主领。请根据以下信息，为两首敬拜诗歌之间撰写连接性的串词。

主日证道主题：'{sermon_title}'
核心经文：'{key_scripture}'
上一首歌：《{prev_song['title']}》，标签：{', '.join(prev_song.get('tags', []))}
上一首歌歌词：
{prev_song['lyrics']}

下一首歌：《{current_song['title']}》，标签：{', '.join(current_song.get('tags', []))}
下一首歌歌词：
{current_song['lyrics']}

请仔细分析两首歌的歌词内容和主题，提供三个不同维度的串词草稿，每个大约50-80字：
1. 【赞美维度】: 侧重于引导会众从上一首歌的主题转向下一首歌的敬拜焦点，结合歌词中的关键意象和情感
2. 【激励维度】: 侧重于鼓励会众，结合证道主题和歌词内容给予属灵的鼓励和盼望
3. 【祷告维度】: 写一段简短的祷告词，可以带领会众开口祷告，融入歌词中的祷告元素

请用中文回答，确保你的串词清晰、有感染力且适合在公共敬拜场合使用。语言要亲切、属灵、适合华人教会的敬拜氛围。
"""

    try:
        response = model.generate_content(prompt)
        content = response.text
        
        lines = content.split('\n')
        dimensions = {}
        current_dimension = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if '【赞美维度】' in line:
                if current_dimension:
                    dimensions[current_dimension] = '\n'.join(current_content).strip()
                current_dimension = "赞美维度"
                current_content = []
            elif '【激励维度】' in line:
                if current_dimension:
                    dimensions[current_dimension] = '\n'.join(current_content).strip()
                current_dimension = "激励维度"
                current_content = []
            elif '【祷告维度】' in line:
                if current_dimension:
                    dimensions[current_dimension] = '\n'.join(current_content).strip()
                current_dimension = "祷告维度"
                current_content = []
            elif line and current_dimension:
                current_content.append(line)
        
        if current_dimension and current_content:
            dimensions[current_dimension] = '\n'.join(current_content).strip()
        
        if not dimensions:
            dimensions = {"通用串词": content}
        
        return dimensions
        
    except Exception as e:
        raise Exception(f"API调用失败: {e}")

def generate_opening_transition(sermon_title, key_scripture, song):
    model = config.get_model()
    
    prompt = f"""你是一位经验丰富的、属灵的基督徒敬拜主领。擅长用简短、有感染力的语言，在敬拜开始前引导会众的内心进入敬拜的状态。
    请根据以下信息，为敬拜聚会的开场撰写引导词，引入第一首敬拜诗歌。

主日证道主题：'{sermon_title}'
核心经文：'{key_scripture}'
开场诗歌：《{song['title']}》，标签：{', '.join(song.get('tags', []))}
开场诗歌歌词：
{song['lyrics']}

请仔细分析开场诗歌的歌词内容和主题，提供三个不同维度的开场引导词，每个大约80-120字：
1. 【欢迎维度】: 温暖地欢迎会众，营造敬拜氛围，引导大家准备心灵敬拜神，结合歌词中的敬拜元素
2. 【主题维度】: 结合证道主题、经文和歌词内容，引导会众进入今日的属灵焦点
3. 【祷告维度】: 以祷告的方式开始，求神的同在和祝福，融入歌词中的祷告元素，然后引入诗歌

请用中文回答，确保你的串词清晰、有感染力且适合在公共敬拜场合使用。语言要亲切、属灵、适合华人教会的敬拜氛围。
"""

    try:
        response = model.generate_content(prompt)
        content = response.text
        
        lines = content.split('\n')
        dimensions = {}
        current_dimension = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if '【欢迎维度】' in line:
                if current_dimension:
                    dimensions[current_dimension] = '\n'.join(current_content).strip()
                current_dimension = "欢迎维度"
                current_content = []
            elif '【主题维度】' in line:
                if current_dimension:
                    dimensions[current_dimension] = '\n'.join(current_content).strip()
                current_dimension = "主题维度"
                current_content = []
            elif '【祷告维度】' in line:
                if current_dimension:
                    dimensions[current_dimension] = '\n'.join(current_content).strip()
                current_dimension = "祷告维度"
                current_content = []
            elif line and current_dimension:
                current_content.append(line)
        
        if current_dimension and current_content:
            dimensions[current_dimension] = '\n'.join(current_content).strip()
        
        if not dimensions:
            dimensions = {"通用开场词": content}
        
        return dimensions
        
    except Exception as e:
        raise Exception(f"API调用失败: {e}")

def rehearsal_mode():
    st.header("🎭 敬拜排练模式")
    
    if 'rehearsal_flow' not in st.session_state:
        st.warning("没有找到敬拜流程数据，请先在设计器中创建流程。")
        if st.button("返回设计器"):
            st.session_state.page = "flow_designer"
            st.rerun()
        return
    
    flow = st.session_state.rehearsal_flow
    songs = config.load_songs()
    
    # 检查流程是否为空
    if not flow.get('worship_flow') and not flow.get('sermon_title'):
        st.info("📋 **流程信息不完整**\n\n当前流程为空，请返回设计器添加内容：\n- 填写证道主题和核心经文\n- 选择敬拜诗歌\n- 生成串词连接")
        if st.button("🔙 返回设计器"):
            st.session_state.page = "flow_designer"
            st.rerun()
        return
    
    st.write(f"**主日日期:** {flow['date']}")
    st.write(f"**证道主题:** {flow['sermon_title']}")
    st.write(f"**核心经文:** {flow['key_scripture']}")
    st.write("---")
    
    rehearsal_content = []
    rehearsal_content.append(f"# 敬拜流程 - {flow['date']}")
    rehearsal_content.append(f"**证道主题:** {flow['sermon_title']}")
    rehearsal_content.append(f"**核心经文:** {flow['key_scripture']}")
    rehearsal_content.append("\n---\n")
    
    for item in flow.get('worship_flow', []):
        if item['type'] == 'song':
            song = songs.get(item['song_id'])
            if song:
                st.subheader(f"🎵 {song['title']}")
                rehearsal_content.append(f"## {song['title']}")
                if song.get('author'):
                    st.write(f"作者: {song['author']}")
                    rehearsal_content.append(f"**作者:** {song['author']}")
                if song.get('key'):
                    st.write(f"调性: {song['key']}")
                    rehearsal_content.append(f"**调性:** {song['key']}")
                
                st.code(song['lyrics'], language=None)
                rehearsal_content.append(f"```\n{song['lyrics']}\n```")
                rehearsal_content.append("")
        
        elif item['type'] == 'transition_text':
            dimension = item.get('dimension', '串词')
            transition_type = item.get('transition_type', 'transition')
            
            if transition_type == 'opening':
                st.info(f"🎬 开场 - {dimension}: {item['content']}")
                rehearsal_content.append(f"**开场 - {dimension}:** {item['content']}")
            else:
                st.info(f"🔗 {dimension}: {item['content']}")
                rehearsal_content.append(f"**{dimension}:** {item['content']}")
            rehearsal_content.append("")
        
        st.write("---")
        rehearsal_content.append("---")
    
    st.subheader("📋 完整讲稿")
    full_script = "\n".join(rehearsal_content)
    st.markdown(full_script)
    
    st.download_button(
        label="📥 下载讲稿",
        data=full_script,
        file_name=f"worship_flow_{flow['date']}.md",
        mime="text/markdown"
    )

def main():
    st.title("🎵 灵泉Flow (WorshipFlow)")
    st.markdown("*基于AI的敬拜串词生成系统*")
    
    if 'page' not in st.session_state:
        st.session_state.page = "flow_designer"
    
    st.sidebar.title("导航")
    
    pages = {
        "敬拜流程设计": "flow_designer",
        "诗歌库管理": "song_manager",
        "排练模式": "rehearsal"
    }
    
    for page_name, page_key in pages.items():
        if st.sidebar.button(page_name, key=f"nav_{page_key}"):
            st.session_state.page = page_key
            user_logger.log_page_visit(page_name)
            st.rerun()
    
    st.sidebar.write("---")
    
    # 显示当前系统状态
    st.sidebar.subheader("🤖 系统状态")
    
    # 显示当前模型
    current_model_display = config.get_model_display_name()
    st.sidebar.text(f"模型: {current_model_display}")
    
    # 显示认证信息
    auth_method = getattr(config, 'auth_method', 'unknown')
    auth_display = {"api_key": "API密钥", "service_account": "服务账号", "unknown": "未知"}.get(auth_method, auth_method)
    st.sidebar.text(f"认证: {auth_display}")
    
    # 显示存储信息
    from storage import storage_manager
    storage_status = "本地存储" if not storage_manager.is_gcs_available() else "云端存储"
    st.sidebar.text(f"存储: {storage_status}")
    
    # 显示强制本地存储状态
    force_local = os.getenv('FORCE_LOCAL_STORAGE', 'false').lower() == 'true'
    if force_local:
        st.sidebar.text("🏠 强制本地模式")
    
    st.sidebar.write("---")
    st.sidebar.info("💡 **使用提示:**\n- 先在诗歌库中添加诗歌\n- 在设计器中创建敬拜流程\n- 生成AI串词连接诗歌\n- 使用排练模式查看完整流程")
    
    # Log initial page load
    current_page = st.session_state.page
    if 'logged_pages' not in st.session_state:
        st.session_state.logged_pages = set()
    
    if current_page not in st.session_state.logged_pages:
        page_names = {v: k for k, v in pages.items()}
        page_display_name = page_names.get(current_page, current_page)
        user_logger.log_page_visit(page_display_name)
        st.session_state.logged_pages.add(current_page)
    
    if st.session_state.page == "song_manager":
        song_manager_page()
    elif st.session_state.page == "flow_designer":
        worship_flow_designer()
    elif st.session_state.page == "rehearsal":
        rehearsal_mode()

if __name__ == "__main__":
    main()