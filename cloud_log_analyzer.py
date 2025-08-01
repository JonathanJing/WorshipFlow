#!/usr/bin/env python3
"""
Cloud Logging Analysis Tool for WorshipFlow
WorshipFlow云端日志分析工具

This script analyzes user action logs from Google Cloud Logging.
该脚本分析Google Cloud Logging中的用户操作日志。
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional

try:
    from google.cloud import logging as gcp_logging
    from google.auth import default
    GCP_LOGGING_AVAILABLE = True
except ImportError:
    GCP_LOGGING_AVAILABLE = False


class CloudLogAnalyzer:
    """
    Analyzes WorshipFlow logs from Google Cloud Logging
    分析Google Cloud Logging中的WorshipFlow日志
    """
    
    def __init__(self, project_id: Optional[str] = None):
        """
        Initialize cloud log analyzer
        初始化云端日志分析器
        
        Args:
            project_id: GCP project ID / GCP项目ID
        """
        if not GCP_LOGGING_AVAILABLE:
            raise ImportError("Google Cloud Logging library not available")
        
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        if not self.project_id:
            raise ValueError("Project ID required. Set GOOGLE_CLOUD_PROJECT or pass project_id")
        
        self.client = gcp_logging.Client(project=self.project_id)
        self.logs = []
    
    def fetch_logs(self, hours_back: int = 24, filter_query: Optional[str] = None) -> int:
        """
        Fetch logs from Cloud Logging
        从Cloud Logging获取日志
        
        Args:
            hours_back: Hours to look back / 回溯小时数
            filter_query: Additional filter query / 额外过滤查询
            
        Returns:
            int: Number of log entries fetched / 获取的日志条目数
        """
        self.logs = []
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        
        # Build filter query
        base_filter = f'''
        logName="projects/{self.project_id}/logs/worship-flow-user-actions"
        timestamp >= "{start_time.isoformat()}Z"
        timestamp <= "{end_time.isoformat()}Z"
        '''
        
        if filter_query:
            base_filter += f" AND {filter_query}"
        
        try:
            # Fetch logs
            entries = self.client.list_entries(filter_=base_filter.strip())
            
            for entry in entries:
                try:
                    # Extract structured payload
                    if hasattr(entry, 'payload') and entry.payload:
                        log_data = dict(entry.payload)
                        log_data['timestamp'] = entry.timestamp.isoformat()
                        log_data['severity'] = entry.severity
                        self.logs.append(log_data)
                except Exception as e:
                    print(f"Error processing log entry: {e}")
                    continue
            
            print(f"Fetched {len(self.logs)} log entries from Cloud Logging")
            return len(self.logs)
            
        except Exception as e:
            print(f"Error fetching logs from Cloud Logging: {e}")
            return 0
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics / 获取使用统计"""
        if not self.logs:
            return {}
        
        users = set()
        sessions = set()
        categories = Counter()
        actions = Counter()
        
        for log in self.logs:
            users.add(log.get('user_id', 'unknown'))
            sessions.add(log.get('session_id', 'unknown'))
            categories[log.get('category', 'unknown')] += 1
            actions[log.get('action', 'unknown')] += 1
        
        return {
            "unique_users": len(users),
            "unique_sessions": len(sessions),
            "total_actions": len(self.logs),
            "categories": dict(categories),
            "top_actions": dict(actions.most_common(10))
        }
    
    def get_ai_performance(self) -> Dict[str, Any]:
        """Get AI performance metrics / 获取AI性能指标"""
        ai_logs = [log for log in self.logs if log.get('category') == 'ai_generation']
        
        if not ai_logs:
            return {"message": "No AI generation logs found"}
        
        model_usage = Counter()
        success_rate = defaultdict(list)
        error_types = Counter()
        
        for log in ai_logs:
            details = log.get('details', {})
            model_name = details.get('model_name', 'unknown')
            prompt_type = details.get('prompt_type', 'unknown')
            success = details.get('success', False)
            
            model_usage[model_name] += 1
            success_rate[prompt_type].append(success)
            
            if not success:
                error = details.get('error', 'unknown')
                error_types[error] += 1
        
        # Calculate success rates
        success_rates = {}
        for prompt_type, results in success_rate.items():
            total = len(results)
            successful = sum(results)
            success_rates[prompt_type] = {
                'success_rate': successful / total if total > 0 else 0,
                'total_attempts': total,
                'successful': successful
            }
        
        return {
            "total_ai_requests": len(ai_logs),
            "model_usage": dict(model_usage),
            "success_rates": success_rates,
            "common_errors": dict(error_types.most_common(5))
        }
    
    def get_user_behavior(self) -> Dict[str, Any]:
        """Get user behavior analysis / 获取用户行为分析"""
        page_visits = Counter()
        user_sessions = defaultdict(list)
        
        for log in self.logs:
            if log.get('action') == 'page_visit':
                page_name = log.get('details', {}).get('page_name', 'unknown')
                page_visits[page_name] += 1
            
            user_id = log.get('user_id', 'unknown')
            user_sessions[user_id].append({
                'action': log.get('action'),
                'category': log.get('category'),
                'timestamp': log.get('timestamp')
            })
        
        # Calculate average session length
        session_lengths = []
        for user_actions in user_sessions.values():
            if len(user_actions) > 1:
                sorted_actions = sorted(user_actions, key=lambda x: x['timestamp'])
                start = datetime.fromisoformat(sorted_actions[0]['timestamp'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(sorted_actions[-1]['timestamp'].replace('Z', '+00:00'))
                session_lengths.append((end - start).total_seconds() / 60)  # minutes
        
        avg_session_length = sum(session_lengths) / len(session_lengths) if session_lengths else 0
        
        return {
            "page_visits": dict(page_visits),
            "most_popular_page": page_visits.most_common(1)[0] if page_visits else None,
            "active_users": len(user_sessions),
            "average_session_length_minutes": round(avg_session_length, 2),
            "actions_per_user": {
                user_id: len(actions) 
                for user_id, actions in user_sessions.items()
            }
        }
    
    def generate_cloud_report(self) -> str:
        """
        Generate comprehensive report from Cloud Logging data
        从Cloud Logging数据生成综合报告
        
        Returns:
            str: Report content / 报告内容
        """
        if not self.logs:
            return "No log data available from Cloud Logging"
        
        usage_stats = self.get_usage_stats()
        ai_performance = self.get_ai_performance()
        user_behavior = self.get_user_behavior()
        
        report = f"""
# WorshipFlow Cloud Logging 分析报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
项目: {self.project_id}

## 📊 总体使用统计
- 独立用户数: {usage_stats.get('unique_users', 0)}
- 独立会话数: {usage_stats.get('unique_sessions', 0)}
- 总操作数: {usage_stats.get('total_actions', 0)}

## 📱 操作类别分布
"""
        
        for category, count in usage_stats.get('categories', {}).items():
            report += f"- {category}: {count} 次\n"
        
        report += f"""
## 🎯 热门操作
"""
        
        for action, count in usage_stats.get('top_actions', {}).items():
            report += f"- {action}: {count} 次\n"
        
        if ai_performance.get('total_ai_requests', 0) > 0:
            report += f"""
## 🤖 AI 性能分析
- AI请求总数: {ai_performance['total_ai_requests']}
- 模型使用分布:
"""
            
            for model, count in ai_performance.get('model_usage', {}).items():
                report += f"  - {model}: {count} 次\n"
            
            report += "- 功能成功率:\n"
            for prompt_type, stats in ai_performance.get('success_rates', {}).items():
                success_rate = stats['success_rate'] * 100
                report += f"  - {prompt_type}: {success_rate:.1f}% ({stats['successful']}/{stats['total_attempts']})\n"
        
        report += f"""
## 👥 用户行为分析
- 活跃用户数: {user_behavior.get('active_users', 0)}
- 平均会话时长: {user_behavior.get('average_session_length_minutes', 0)} 分钟
- 最受欢迎页面: {user_behavior.get('most_popular_page', ('无', 0))[0]} ({user_behavior.get('most_popular_page', ('无', 0))[1]} 次访问)

## 📄 页面访问分布
"""
        
        for page, count in user_behavior.get('page_visits', {}).items():
            report += f"- {page}: {count} 次\n"
        
        return report
    
    def export_raw_data(self, output_file: str):
        """
        Export raw log data to JSON file
        将原始日志数据导出到JSON文件
        
        Args:
            output_file: Output file path / 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"Raw log data exported to: {output_file}")


def main():
    """Main function for command line usage / 命令行使用的主函数"""
    if not GCP_LOGGING_AVAILABLE:
        print("Error: Google Cloud Logging library not available")
        print("Install with: pip install google-cloud-logging")
        return
    
    parser = argparse.ArgumentParser(description='WorshipFlow云端日志分析工具')
    parser.add_argument('--project-id', help='GCP项目ID')
    parser.add_argument('--hours', type=int, default=24, help='回溯小时数 (默认24)')
    parser.add_argument('--filter', help='额外过滤条件')
    parser.add_argument('--output', help='输出报告文件路径')
    parser.add_argument('--export-raw', help='导出原始数据JSON文件路径')
    
    args = parser.parse_args()
    
    try:
        analyzer = CloudLogAnalyzer(args.project_id)
        
        if analyzer.fetch_logs(args.hours, args.filter) == 0:
            print("No logs found in Cloud Logging")
            return
        
        # Generate report
        report = analyzer.generate_cloud_report()
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to: {args.output}")
        else:
            print(report)
        
        # Export raw data if requested
        if args.export_raw:
            analyzer.export_raw_data(args.export_raw)
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()