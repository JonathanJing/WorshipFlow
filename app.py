import streamlit as st
import json
import os
from datetime import datetime
from config import Config

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
    st.header("🎵 诗歌库管理")
    
    tab1, tab2 = st.tabs(["添加新歌", "查看诗歌"])
    
    with tab1:
        st.subheader("添加新诗歌")
        
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
                        st.success(f"诗歌 '{title}' 已保存!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"保存失败: {e}")
    
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
    st.header("✨ 敬拜流程设计器")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("主日信息")
        sermon_title = st.text_input("证道主题 *", placeholder="例如: 行在光明中")
        key_scripture = st.text_input("核心经文 *", placeholder="例如: 约翰一书 1:7")
        service_date = st.date_input("主日日期", datetime.now())
    
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
    
    if sermon_title and key_scripture and selected_songs:
        st.write("---")
        st.subheader("🎼 敬拜流程预览")
        
        if 'flow_data' not in st.session_state:
            st.session_state.flow_data = {
                "date": str(service_date),
                "sermon_title": sermon_title,
                "key_scripture": key_scripture,
                "worship_flow": []
            }
        
        for i, song_id in enumerate(selected_songs):
            song = songs[song_id]
            
            st.write(f"### {i+1}. {song['title']}")
            
            if i > 0:
                col1, col2 = st.columns([3, 1])
                with col1:
                    if f"transition_{i}" in st.session_state:
                        st.write("**生成的串词:**")
                        for dimension, content in st.session_state[f"transition_{i}"].items():
                            with st.expander(f"{dimension}"):
                                st.write(content)
                                if st.button(f"使用此串词", key=f"use_{i}_{dimension}"):
                                    st.session_state[f"selected_transition_{i}"] = content
                                    st.success("串词已选择!")
                
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
                                st.rerun()
                            except Exception as e:
                                st.error(f"生成串词失败: {e}")
            
            with st.expander(f"查看 '{song['title']}' 详情"):
                st.write(f"**作者:** {song.get('author', '未知')}")
                st.write(f"**调性:** {song.get('key', '未指定')}")
                st.write(f"**标签:** {', '.join(song.get('tags', []))}")
                st.text(song['lyrics'])
        
        st.write("---")
        if st.button("💾 保存敬拜流程"):
            flow_id = f"{service_date}_service"
            
            flow_items = []
            for i, song_id in enumerate(selected_songs):
                if i > 0 and f"selected_transition_{i}" in st.session_state:
                    flow_items.append({
                        "type": "transition_text",
                        "content": st.session_state[f"selected_transition_{i}"]
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
            
            try:
                config.save_flow(flow_id, flow_data)
                st.success("敬拜流程已保存!")
                
                if st.button("🎭 进入排练模式"):
                    st.session_state.rehearsal_flow = flow_data
                    st.session_state.page = "rehearsal"
                    st.rerun()
            except Exception as e:
                st.error(f"保存失败: {e}")

def generate_transitions(sermon_title, key_scripture, prev_song, current_song):
    model = config.get_model()
    
    prompt = f"""你是一位非常有经验的、属灵的基督徒敬拜主领。请根据以下信息，为两首敬拜诗歌之间撰写连接性的串词。

主日证道主题：'{sermon_title}'
核心经文：'{key_scripture}'
上一首歌：《{prev_song['title']}》，标签：{', '.join(prev_song.get('tags', []))}
下一首歌：《{current_song['title']}》，标签：{', '.join(current_song.get('tags', []))}

请提供三个不同维度的串词草稿，每个大约50-80字：
1. 【赞美维度】: 侧重于引导会众从上一首歌的主题转向下一首歌的敬拜焦点
2. 【激励维度】: 侧重于鼓励会众，结合证道主题给予属灵的鼓励和盼望
3. 【祷告维度】: 写一段简短的祷告词，可以带领会众开口祷告

请用中文回答，语言要亲切、属灵、适合华人教会的敬拜氛围。"""

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
    
    st.write(f"**主日日期:** {flow['date']}")
    st.write(f"**证道主题:** {flow['sermon_title']}")
    st.write(f"**核心经文:** {flow['key_scripture']}")
    st.write("---")
    
    rehearsal_content = []
    rehearsal_content.append(f"# 敬拜流程 - {flow['date']}")
    rehearsal_content.append(f"**证道主题:** {flow['sermon_title']}")
    rehearsal_content.append(f"**核心经文:** {flow['key_scripture']}")
    rehearsal_content.append("\n---\n")
    
    for i, item in enumerate(flow.get('worship_flow', [])):
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
            st.info(f"串词: {item['content']}")
            rehearsal_content.append(f"**串词:** {item['content']}")
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
            st.rerun()
    
    st.sidebar.write("---")
    st.sidebar.info("💡 **使用提示:**\n- 先在诗歌库中添加诗歌\n- 在设计器中创建敬拜流程\n- 生成AI串词连接诗歌\n- 使用排练模式查看完整流程")
    
    if st.session_state.page == "song_manager":
        song_manager_page()
    elif st.session_state.page == "flow_designer":
        worship_flow_designer()
    elif st.session_state.page == "rehearsal":
        rehearsal_mode()

if __name__ == "__main__":
    main()