#!/usr/bin/env python3
"""
Log Analysis Tool for WorshipFlow
WorshipFlow日志分析工具

This script analyzes user action logs to provide insights about app usage.
该脚本分析用户操作日志以提供应用使用洞察。
"""

import json
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional
import argparse


class WorshipFlowLogAnalyzer:
    """
    Analyzes WorshipFlow user action logs
    分析WorshipFlow用户操作日志
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize log analyzer
        初始化日志分析器
        
        Args:
            log_dir: Directory containing log files / 包含日志文件的目录
        """
        self.log_dir = log_dir
        self.logs = []
    
    def load_logs(self, date_filter: Optional[str] = None) -> int:
        """
        Load logs from files
        从文件加载日志
        
        Args:
            date_filter: Date filter in YYYY-MM-DD format / YYYY-MM-DD格式的日期过滤器
            
        Returns:
            int: Number of log entries loaded / 加载的日志条目数
        """
        self.logs = []
        
        if not os.path.exists(self.log_dir):
            print(f"日志目录不存在: {self.log_dir}")
            return 0
        
        log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.log')]
        
        if date_filter:
            log_files = [f for f in log_files if date_filter in f]
        
        for log_file in sorted(log_files):
            file_path = os.path.join(self.log_dir, log_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        # Extract JSON part from log line
                        # 从日志行中提取JSON部分
                        json_match = re.search(r'INFO - (.+)$', line.strip())
                        if json_match:
                            log_entry = json.loads(json_match.group(1))
                            self.logs.append(log_entry)
                    except (json.JSONDecodeError, AttributeError):
                        continue
        
        print(f"加载了 {len(self.logs)} 条日志记录")
        return len(self.logs)
    
    def get_user_stats(self) -> Dict[str, Any]:
        """
        Get user statistics
        获取用户统计信息
        
        Returns:
            Dict: User statistics / 用户统计信息
        """
        users = set()
        sessions = set()
        
        for log in self.logs:
            users.add(log.get('user_id', 'unknown'))
            sessions.add(log.get('session_id', 'unknown'))
        
        return {
            "unique_users": len(users),
            "unique_sessions": len(sessions),
            "total_actions": len(self.logs)
        }
    
    def get_page_analytics(self) -> Dict[str, Any]:
        """
        Get page visit analytics
        获取页面访问分析
        
        Returns:
            Dict: Page analytics / 页面分析
        """
        page_visits = Counter()
        user_page_visits = defaultdict(Counter)
        
        for log in self.logs:
            if log.get('category') == 'navigation' and log.get('action') == 'page_visit':
                page_name = log.get('details', {}).get('page_name', 'unknown')
                user_id = log.get('user_id', 'unknown')
                
                page_visits[page_name] += 1
                user_page_visits[user_id][page_name] += 1
        
        return {
            "page_visits": dict(page_visits),
            "most_visited_page": page_visits.most_common(1)[0] if page_visits else None,
            "user_page_preferences": dict(user_page_visits)
        }
    
    def get_song_analytics(self) -> Dict[str, Any]:
        """
        Get song management analytics
        获取诗歌管理分析
        
        Returns:
            Dict: Song analytics / 诗歌分析
        """
        song_actions = Counter()
        added_songs = []
        viewed_songs = Counter()
        
        for log in self.logs:
            if log.get('category') == 'song_management':
                action = log.get('action')
                details = log.get('details', {})
                
                song_actions[action] += 1
                
                if action == 'song_added':
                    added_songs.append({
                        'title': details.get('song_title'),
                        'author': details.get('song_author'),
                        'tags': details.get('song_tags', []),
                        'timestamp': log.get('timestamp')
                    })
                elif action == 'song_viewed':
                    viewed_songs[details.get('song_title', 'unknown')] += 1
        
        return {
            "song_actions": dict(song_actions),
            "songs_added": len(added_songs),
            "added_songs_list": added_songs,
            "most_viewed_songs": dict(viewed_songs.most_common(10)),
            "popular_tags": self._get_popular_tags(added_songs)
        }
    
    def get_ai_analytics(self) -> Dict[str, Any]:
        """
        Get AI generation analytics
        获取AI生成分析
        
        Returns:
            Dict: AI analytics / AI分析
        """
        ai_actions = Counter()
        model_usage = Counter()
        success_rate = defaultdict(list)
        prompt_types = Counter()
        
        for log in self.logs:
            if log.get('category') == 'ai_generation':
                action = log.get('action')
                details = log.get('details', {})
                
                ai_actions[action] += 1
                model_usage[details.get('model_name', 'unknown')] += 1
                prompt_types[details.get('prompt_type', 'unknown')] += 1
                
                success = details.get('success', False)
                success_rate[details.get('prompt_type', 'unknown')].append(success)
        
        # Calculate success rates
        success_rates = {}
        for prompt_type, results in success_rate.items():
            success_rates[prompt_type] = {
                'success_rate': sum(results) / len(results) if results else 0,
                'total_attempts': len(results),
                'successful': sum(results)
            }
        
        return {
            "ai_actions": dict(ai_actions),
            "model_usage": dict(model_usage),
            "prompt_types": dict(prompt_types),
            "success_rates": success_rates
        }
    
    def get_flow_analytics(self) -> Dict[str, Any]:
        """
        Get worship flow analytics
        获取敬拜流程分析
        
        Returns:
            Dict: Flow analytics / 流程分析
        """
        flow_actions = Counter()
        saved_flows = []
        
        for log in self.logs:
            if log.get('category') == 'flow_design':
                action = log.get('action')
                details = log.get('details', {})
                
                flow_actions[action] += 1
                
                if action == 'flow_saved':
                    saved_flows.append({
                        'sermon_title': details.get('sermon_title'),
                        'scripture': details.get('key_scripture'),
                        'song_count': details.get('song_count', 0),
                        'has_transitions': details.get('has_transitions', False),
                        'timestamp': log.get('timestamp')
                    })
        
        return {
            "flow_actions": dict(flow_actions),
            "flows_created": len(saved_flows),
            "avg_songs_per_flow": sum(f['song_count'] for f in saved_flows) / len(saved_flows) if saved_flows else 0,
            "flows_with_ai_transitions": sum(1 for f in saved_flows if f['has_transitions']),
            "recent_flows": saved_flows[-10:]  # Last 10 flows
        }
    
    def get_error_analytics(self) -> Dict[str, Any]:
        """
        Get error analytics
        获取错误分析
        
        Returns:
            Dict: Error analytics / 错误分析
        """
        errors = Counter()
        error_details = []
        
        for log in self.logs:
            if log.get('category') == 'error':
                details = log.get('details', {})
                error_type = details.get('error_type', 'unknown')
                
                errors[error_type] += 1
                error_details.append({
                    'type': error_type,
                    'message': details.get('error_message', ''),
                    'context': details.get('context', {}),
                    'timestamp': log.get('timestamp'),
                    'user_id': log.get('user_id')
                })
        
        return {
            "error_counts": dict(errors),
            "total_errors": len(error_details),
            "recent_errors": error_details[-10:]  # Last 10 errors
        }
    
    def _get_popular_tags(self, songs: List[Dict]) -> Counter:
        """Get popular song tags / 获取热门诗歌标签"""
        tag_counter = Counter()
        for song in songs:
            for tag in song.get('tags', []):
                tag_counter[tag] += 1
        return tag_counter
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate comprehensive analytics report
        生成综合分析报告
        
        Args:
            output_file: Output file path / 输出文件路径
            
        Returns:
            str: Report content / 报告内容
        """
        if not self.logs:
            return "没有日志数据可供分析"
        
        # Get all analytics
        user_stats = self.get_user_stats()
        page_analytics = self.get_page_analytics()
        song_analytics = self.get_song_analytics()
        ai_analytics = self.get_ai_analytics()
        flow_analytics = self.get_flow_analytics()
        error_analytics = self.get_error_analytics()
        
        # Generate report
        report = f"""
# WorshipFlow 使用分析报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 用户统计
- 独立用户数: {user_stats['unique_users']}
- 独立会话数: {user_stats['unique_sessions']}
- 总操作数: {user_stats['total_actions']}

## 📱 页面访问统计
- 最受欢迎页面: {page_analytics.get('most_visited_page', ('无', 0))[0]} ({page_analytics.get('most_visited_page', ('无', 0))[1]} 次访问)
- 页面访问分布:
"""
        
        for page, count in page_analytics['page_visits'].items():
            report += f"  - {page}: {count} 次\n"
        
        report += f"""
## 🎵 诗歌管理统计
- 添加诗歌数: {song_analytics['songs_added']}
- 最受欢迎诗歌:
"""
        
        for song, count in list(song_analytics['most_viewed_songs'].items())[:5]:
            report += f"  - {song}: {count} 次查看\n"
        
        if song_analytics['popular_tags']:
            report += "- 热门标签:\n"
            for tag, count in song_analytics['popular_tags'].most_common(10):
                report += f"  - {tag}: {count} 次\n"
        
        report += f"""
## 🤖 AI 生成统计
- 模型使用分布:
"""
        
        for model, count in ai_analytics['model_usage'].items():
            report += f"  - {model}: {count} 次\n"
        
        report += "- AI功能成功率:\n"
        for prompt_type, stats in ai_analytics['success_rates'].items():
            success_rate = stats['success_rate'] * 100
            report += f"  - {prompt_type}: {success_rate:.1f}% ({stats['successful']}/{stats['total_attempts']})\n"
        
        report += f"""
## 📝 敬拜流程统计
- 创建流程数: {flow_analytics['flows_created']}
- 平均每个流程诗歌数: {flow_analytics['avg_songs_per_flow']:.1f}
- 使用AI串词的流程: {flow_analytics['flows_with_ai_transitions']}

## ❌ 错误统计
- 总错误数: {error_analytics['total_errors']}
- 错误类型分布:
"""
        
        for error_type, count in error_analytics['error_counts'].items():
            report += f"  - {error_type}: {count} 次\n"
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"报告已保存到: {output_file}")
        
        return report


def main():
    """Main function for command line usage / 命令行使用的主函数"""
    parser = argparse.ArgumentParser(description='WorshipFlow日志分析工具')
    parser.add_argument('--log-dir', default='logs', help='日志文件目录')
    parser.add_argument('--date', help='分析特定日期的日志 (YYYY-MM-DD)')
    parser.add_argument('--output', help='输出报告文件路径')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')
    
    args = parser.parse_args()
    
    analyzer = WorshipFlowLogAnalyzer(args.log_dir)
    
    if analyzer.load_logs(args.date) == 0:
        print("没有找到日志文件")
        return
    
    if args.format == 'json':
        # Generate JSON report
        data = {
            'user_stats': analyzer.get_user_stats(),
            'page_analytics': analyzer.get_page_analytics(),
            'song_analytics': analyzer.get_song_analytics(),
            'ai_analytics': analyzer.get_ai_analytics(),
            'flow_analytics': analyzer.get_flow_analytics(),
            'error_analytics': analyzer.get_error_analytics()
        }
        
        output = json.dumps(data, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
        else:
            print(output)
    else:
        # Generate text report
        report = analyzer.generate_report(args.output)
        if not args.output:
            print(report)


if __name__ == "__main__":
    main()