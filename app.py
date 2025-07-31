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
    
    # 检查是否有保存成功的状态并显示
    if 'song_save_success' in st.session_state:
        success_info = st.session_state.song_save_success
        
        # 显示持久的成功消息
        success_msg = f"""
        🎉 **诗歌添加成功！**
        
        - **标题:** {success_info['title']}
        - **作者:** {success_info.get('author', '未指定')}
        - **调性:** {success_info.get('key', '未指定')}
        - **标签:** {', '.join(success_info.get('tags', [])) if success_info.get('tags') else '无'}
        - **保存时间:** {success_info['timestamp']}
        - **文件ID:** `{success_info['song_id']}`
        
        你可以在「查看诗歌」标签页中查看刚添加的诗歌，或前往敬拜流程设计页面使用。
        """
        
        st.success(success_msg)
        
        # 提供操作按钮
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📖 查看此诗歌", key="view_added_song"):
                # 切换到查看诗歌标签页并设置选中的诗歌
                st.session_state.selected_song_title = success_info['title']
                # 清除成功状态
                del st.session_state.song_save_success
                st.rerun()
        
        with col2:
            if st.button("🎼 去流程设计", key="goto_flow_design"):
                # 清除成功状态并跳转到流程设计
                del st.session_state.song_save_success
                st.session_state.page = "flow_designer"
                st.rerun()
        
        with col3:
            if st.button("✅ 确认已知晓", key="dismiss_song_success"):
                del st.session_state.song_save_success
                st.rerun()
    
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
                        
                        # 设置成功状态以便显示消息
                        st.session_state.song_save_success = {
                            'song_id': song_id,
                            'title': title,
                            'author': author,
                            'key': key,
                            'tags': tags,
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        # 重新运行以显示成功状态
                        st.rerun()
                        
                    except Exception as e:
                        # Log error
                        user_logger.log_error("song_save_failed", str(e), {"song_title": title})
                        st.error(f"❌ 保存失败: {e}\n\n请检查:\n- 网络连接是否正常\n- 存储权限是否正确\n- 诗歌信息是否完整")
    
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
            
            # 检查是否有预选的诗歌（从成功消息跳转过来的）
            default_index = 0
            if 'selected_song_title' in st.session_state:
                try:
                    default_index = song_titles.index(st.session_state.selected_song_title)
                    # 清除预选状态
                    del st.session_state.selected_song_title
                except ValueError:
                    # 如果找不到预选的诗歌，使用默认值
                    default_index = 0
            
            selected_title = st.selectbox("选择诗歌", song_titles, index=default_index)
            
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
    
    # 检查是否有保存成功的状态并显示
    if 'flow_save_success' in st.session_state:
        success_info = st.session_state.flow_save_success
        
        # 显示持久的成功消息
        st.success(f"""
        🎉 **流程保存成功！**
        
        - **流程ID:** {success_info['flow_id']}
        - **保存时间:** {success_info['timestamp']}
        - **诗歌数量:** {success_info['song_count']} 首
        - **AI串词:** {success_info['transition_count']} 个
        
        你可以继续编辑当前流程或进入排练模式查看完整内容。
        """)
        
        # 提供清除成功消息的选项
        if st.button("✅ 确认已知晓", key="dismiss_success"):
            del st.session_state.flow_save_success
            st.rerun()
    
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
                    
                    # 显示详细的成功信息
                    success_msg = f"✅ **敬拜流程保存成功！**\n\n"
                    success_msg += f"**主题:** {sermon_title}\n"
                    success_msg += f"**经文:** {key_scripture}\n"
                    success_msg += f"**日期:** {service_date}\n"
                    success_msg += f"**诗歌数量:** {len(selected_songs)} 首\n"
                    
                    # 统计生成的串词数量
                    transition_count = len([item for item in flow_items if item.get('type') == 'transition_text'])
                    if transition_count > 0:
                        success_msg += f"**AI串词:** {transition_count} 个\n"
                    
                    success_msg += f"**流程ID:** {flow_id}\n"
                    success_msg += f"**保存时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    
                    st.success(success_msg)
                    
                    # 显示后续操作提示
                    st.info("💡 **接下来你可以:**\n- 点击「🎭 进入排练模式」查看完整流程\n- 在「排练模式」页面下载讲稿\n- 继续修改当前流程或创建新流程")
                    
                    # 设置成功状态以便显示消息
                    st.session_state.flow_save_success = {
                        'flow_id': flow_id,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'song_count': len(selected_songs),
                        'transition_count': transition_count
                    }
                    
                except Exception as e:
                    # Log error
                    user_logger.log_error("flow_save_failed", str(e), {
                        "sermon_title": sermon_title,
                        "flow_id": flow_id
                    })
                    st.error(f"❌ 保存失败: {e}\n\n请检查:\n- 网络连接是否正常\n- 存储权限是否正确\n- 所有必填信息是否完整")
        
        with col2:
            if st.button("🎭 进入排练模式", use_container_width=True):
                # 记录用户进入排练模式
                user_logger.log_action("enter_rehearsal_mode", {
                    "sermon_title": sermon_title,
                    "song_count": len(selected_songs),
                    "from_page": "flow_designer"
                }, "navigation")
                
                st.session_state.page = "rehearsal"
                st.rerun()
    
    else:
        # 即使没有完成所有步骤，也存储基础数据并提供排练模式入口
        st.session_state.rehearsal_flow = basic_flow_data
        
        st.write("---")
        st.info("💡 **提示:** 填写证道主题、核心经文并选择诗歌后，可以查看完整的敬拜流程预览")
        
        if st.button("🎭 进入排练模式", help="即使流程未完成也可以预览"):
            # 记录用户进入排练模式（未完成流程）
            user_logger.log_action("enter_rehearsal_mode", {
                "sermon_title": st.session_state.get('sermon_title', 'incomplete'),
                "flow_status": "incomplete",
                "from_page": "flow_designer"
            }, "navigation")
            
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
    
    # 添加历史流程加载功能
    st.subheader("📋 流程选择")
    
    # 创建两个选项卡：当前流程和历史流程
    tab1, tab2 = st.tabs(["当前流程", "历史流程"])
    
    with tab1:
        # 当前流程逻辑（原有的）
        if 'rehearsal_flow' not in st.session_state:
            st.warning("没有找到当前敬拜流程数据，请先在设计器中创建流程。")
            if st.button("返回设计器", key="return_to_designer_current"):
                st.session_state.page = "flow_designer"
                st.rerun()
            return
        else:
            flow = st.session_state.rehearsal_flow
            st.info(f"📅 当前流程：{flow.get('sermon_title', '未命名')} - {flow.get('date', '未知日期')}")
    
    with tab2:
        # 历史流程加载功能
        st.write("🗂️ **从历史记录中加载敬拜流程**")
        
        # 快速加载功能
        with st.expander("⚡ 快速加载 - 通过流程ID", expanded=False):
            st.write("如果您知道确切的流程ID，可以直接输入快速加载：")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                quick_flow_id = st.text_input(
                    "流程ID", 
                    placeholder="例如: 2025-07-30_143022_service",
                    key="quick_flow_id",
                    help="流程ID格式通常为：日期_时间_service"
                )
            
            with col2:
                if st.button("🚀 快速加载", key="quick_load_btn"):
                    if quick_flow_id:
                        try:
                            all_flows = config.load_flows()
                            
                            if quick_flow_id in all_flows:
                                flow_data = all_flows[quick_flow_id]
                                st.session_state.rehearsal_flow = flow_data
                                
                                # 记录快速加载
                                user_logger.log_action("quick_flow_loaded", {
                                    "flow_id": quick_flow_id,
                                    "sermon_title": flow_data.get('sermon_title'),
                                    "date": flow_data.get('date'),
                                    "load_method": "quick_id"
                                }, "flow_management")
                                
                                st.success(f"✅ 已快速加载流程：{flow_data.get('sermon_title', '未命名')}")
                                st.rerun()
                            else:
                                st.error(f"❌ 未找到流程ID: {quick_flow_id}")
                                
                                # 建议相似的ID
                                similar_ids = [fid for fid in all_flows.keys() if quick_flow_id.lower() in fid.lower()]
                                if similar_ids:
                                    st.write("💡 **您是否在寻找这些流程？**")
                                    for similar_id in similar_ids[:5]:  # 只显示前5个相似的
                                        flow_data = all_flows[similar_id]
                                        st.write(f"• `{similar_id}` - {flow_data.get('sermon_title', '未命名')}")
                        except Exception as e:
                            st.error(f"❌ 快速加载失败: {e}")
                            user_logger.log_error("quick_flow_load_failed", str(e), {
                                "attempted_flow_id": quick_flow_id
                            })
                    else:
                        st.warning("请输入流程ID")
        
        st.write("---")
        
        # 获取所有历史流程
        try:
            all_flows = config.load_flows()
            
            if not all_flows:
                st.info("📝 暂无历史敬拜流程记录。创建并保存第一个流程后，就可以在这里查看历史记录了。")
                if st.button("前往创建流程", key="goto_create_flow"):
                    st.session_state.page = "flow_designer"
                    st.rerun()
                return
            
            # 按日期排序流程（最新的在前）
            sorted_flows = dict(sorted(all_flows.items(), key=lambda x: x[1].get('date', ''), reverse=True))
            
            st.write(f"📊 找到 **{len(sorted_flows)}** 个历史流程")
            
            # 流程搜索和过滤
            col1, col2 = st.columns([2, 1])
            
            with col1:
                search_term = st.text_input("🔍 搜索流程", placeholder="输入主题、经文或日期关键词...", key="flow_search")
            
            with col2:
                # 日期范围过滤
                date_filter = st.selectbox("📅 日期过滤", ["全部", "最近7天", "最近30天", "最近3个月"], key="date_filter")
            
            # 应用搜索过滤
            filtered_flows = sorted_flows
            
            if search_term:
                filtered_flows = {
                    k: v for k, v in sorted_flows.items()
                    if (search_term.lower() in v.get('sermon_title', '').lower() or
                        search_term.lower() in v.get('key_scripture', '').lower() or
                        search_term.lower() in v.get('date', '').lower())
                }
            
            # 应用日期过滤
            if date_filter != "全部":
                from datetime import datetime, timedelta
                today = datetime.now().date()
                
                if date_filter == "最近7天":
                    cutoff_date = today - timedelta(days=7)
                elif date_filter == "最近30天":
                    cutoff_date = today - timedelta(days=30)
                elif date_filter == "最近3个月":
                    cutoff_date = today - timedelta(days=90)
                
                filtered_flows = {
                    k: v for k, v in filtered_flows.items()
                    if datetime.strptime(v.get('date', '1900-01-01'), '%Y-%m-%d').date() >= cutoff_date
                }
            
            if not filtered_flows:
                st.warning("🔍 没有找到匹配的流程，请尝试其他搜索条件。")
                return
            
            st.write(f"显示 **{len(filtered_flows)}** 个匹配的流程：")
            
            # 显示流程列表
            for flow_id, flow_data in filtered_flows.items():
                with st.expander(f"📋 {flow_data.get('sermon_title', '未命名')} - {flow_data.get('date', '未知日期')}", expanded=False):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**主题:** {flow_data.get('sermon_title', '未命名')}")
                        st.write(f"**经文:** {flow_data.get('key_scripture', '未指定')}")
                        st.write(f"**日期:** {flow_data.get('date', '未知')}")
                        
                        # 统计信息
                        worship_flow = flow_data.get('worship_flow', [])
                        song_count = len([item for item in worship_flow if item.get('type') == 'song'])
                        transition_count = len([item for item in worship_flow if item.get('type') == 'transition_text'])
                        
                        st.write(f"**诗歌数量:** {song_count} 首")
                        st.write(f"**AI串词:** {transition_count} 个")
                    
                    with col2:
                        st.write(f"**流程ID:** `{flow_id}`")
                        
                        # 复制ID按钮
                        if st.button("📋 复制ID", key=f"copy_{flow_id}", help="复制流程ID到剪贴板"):
                            # 使用streamlit的复制功能（如果可用）或显示提示
                            st.info(f"流程ID已复制: `{flow_id}`\n\n您可以在'快速加载'功能中粘贴此ID")
                        
                        # 显示包含的诗歌
                        if worship_flow:
                            songs = []
                            for item in worship_flow:
                                if item.get('type') == 'song':
                                    song_id = item.get('song_id')
                                    songs.append(song_id)
                            
                            if songs:
                                st.write("**包含诗歌:**")
                                # 获取诗歌标题
                                all_songs = config.load_songs()
                                for song_id in songs[:3]:  # 只显示前3首
                                    song_title = all_songs.get(song_id, {}).get('title', song_id)
                                    st.write(f"• {song_title}")
                                if len(songs) > 3:
                                    st.write(f"• ...还有{len(songs)-3}首")
                    
                    with col3:
                        if st.button(f"📥 加载此流程", key=f"load_{flow_id}"):
                            # 加载选中的流程到当前排练模式
                            st.session_state.rehearsal_flow = flow_data
                            
                            # 记录历史流程加载
                            user_logger.log_action("historical_flow_loaded", {
                                "flow_id": flow_id,
                                "sermon_title": flow_data.get('sermon_title'),
                                "date": flow_data.get('date'),
                                "song_count": song_count,
                                "transition_count": transition_count
                            }, "flow_management")
                            
                            st.success(f"✅ 已加载流程：{flow_data.get('sermon_title', '未命名')}")
                            st.rerun()
                        
                        if st.button(f"🗑️ 删除", key=f"delete_{flow_id}"):
                            # 这里可以添加删除确认对话框
                            st.error("删除功能暂时禁用，避免误操作")
            
        except Exception as e:
            st.error(f"❌ 加载历史流程时出错: {e}")
            user_logger.log_error("historical_flow_load_failed", str(e), {"context": "rehearsal_mode"})
            return
    
    # 检查是否有流程数据（当前或历史）
    if 'rehearsal_flow' not in st.session_state:
        return
    
    # 下面是原有的排练模式显示逻辑
    flow = st.session_state.rehearsal_flow
    songs = config.load_songs()
    
    st.write("---")
    
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
    st.markdown("*基于AI的敬拜串词生成系统， 使用大语言模型为敬拜主领生成高质量的敬拜诗歌串词。*")
    
    # 项目介绍展开器
    with st.expander("📖 关于灵泉Flow - 项目介绍", expanded=False):
        st.markdown("""
        ## 🎯 项目概述
        
        **灵泉Flow (WorshipFlow)** 是一个专为华人教会敬拜主领设计的AI智能敬拜流程管理系统。
        通过先进的大语言模型技术，为敬拜主领提供专业、贴切的诗歌串词生成服务。
        
        ---
        
        ## 😰 用户痛点分析
        
        ### 🎤 敬拜主领面临的挑战
        
        #### 1. **串词创作压力大**
        - ⏰ **时间紧迫**：每周需要准备新的敬拜流程，时间有限
        - 💭 **创意枯竭**：长期创作导致灵感不足，串词重复单调
        - 📚 **神学要求高**：需要准确传达圣经真理，不能有神学偏差
        
        #### 2. **流程管理困难**
        - 📋 **流程繁琐**：手动安排诗歌顺序，缺乏系统化管理
        - 🔗 **衔接不自然**：诗歌间过渡生硬，影响敬拜氛围
        - 📝 **记录不完整**：缺乏完整的敬拜流程记录和复用机制
        
        #### 3. **团队协作不便**
        - 👥 **沟通成本高**：与乐手、技术团队沟通不及时
        - 📱 **信息分散**：敬拜流程分散在不同文档中
        - 🔄 **重复劳动**：每次都要从零开始准备
        
        ---
        
        ## 🚀 项目目标
        
        ### 🎯 核心目标
        
        #### 1. **智能化串词生成**
        - 🤖 **AI驱动**：基于Gemini大语言模型，生成高质量串词
        - 📖 **神学准确**：确保串词内容符合基督教信仰和神学原则
        - 🎨 **多维度选择**：提供赞美、激励、祷告等不同维度的串词风格
        
        #### 2. **系统化流程管理**
        - 📚 **诗歌库管理**：统一管理教会诗歌资源，支持标签分类
        - 🎼 **流程设计**：可视化的敬拜流程设计界面
        - 💾 **数据持久化**：支持本地存储和云端同步
        
        #### 3. **协作友好的工具**
        - 📋 **排练模式**：生成完整的敬拜流程讲稿
        - 📥 **导出功能**：支持Markdown格式导出，便于分享
        - 🔄 **流程复用**：历史流程可查看和复用
        
        ### 🌟 预期成果
        
        #### 对敬拜主领的帮助
        - ⏱️ **节省时间**：将串词准备时间从2-3小时缩短到30分钟
        - 💡 **激发创意**：AI提供多样化的串词建议，激发新的创作思路
        - 📈 **提升质量**：确保串词内容的神学准确性和文学品质
        - 🎯 **聚焦重点**：让主领专注于属灵引导而非文字创作
        
        #### 对教会的价值
        - 🏛️ **标准化流程**：建立教会敬拜流程的标准化管理
        - 📊 **数据积累**：积累敬拜数据，优化教会敬拜体验
        - 👥 **团队效率**：提升敬拜团队的整体协作效率
        - 🌱 **传承发展**：为新主领提供学习和参考资源
        
        ---
        
        ## 🛠 技术特色
        
        - **🧠 智能AI**：集成Google Gemini 2.5 Flash模型
        - **☁️ 云端部署**：支持Google Cloud Run无服务器部署
        - **🔒 数据安全**：本地+云端双重存储，确保数据安全
        - **📊 使用分析**：完整的用户行为日志和数据分析
        - **🌐 现代架构**：基于Streamlit的现代Web应用架构
        
        ---
        
        ## 💝 使命愿景
        
        **使命**：用技术服务教会，让每一次敬拜都更加美好
        
        **愿景**：成为华人教会敬拜主领的得力助手，推动教会敬拜事工的数字化转型
        
        ---
        
        ## 📞 联系与反馈
        
        我们诚挚邀请您的宝贵意见和建议：
        
        - 💬 **功能建议**：您希望添加哪些新功能？
        - 🐛 **问题反馈**：使用中遇到任何问题，请告诉我们
        - 🙏 **使用体验**：分享您的使用感受和改进建议
        - ⛪ **教会需求**：您的教会还有哪些数字化需求？
        
        **反馈方式**：
        - 📧 Email: feedback@worshipflow.ai
        - 💬 微信: WorshipFlow
        - 📱 电话: 400-XXX-XXXX
        
        ---
        
        *感谢您选择灵泉Flow，愿神祝福您的敬拜事工！* 🙏
        """)
        
        # 记录用户查看项目介绍
        if st.button("👍 我已了解项目背景", key="acknowledge_intro"):
            user_logger.log_action("project_intro_viewed", {
                "user_acknowledgment": True,
                "timestamp": datetime.now().isoformat()
            }, "engagement")
            st.success("感谢您的关注！如有任何建议，欢迎随时联系我们。")
    
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