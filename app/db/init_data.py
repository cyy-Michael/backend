"""
数据库初始化脚本
用于初始化数据库表结构和示例数据
"""

import uuid
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取数据库连接信息
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://0227_wx201383_db_user:hdkkdbdikwksbffkfjdwl645s87jwksadasfsafasf@cluster0.roe7na.mongodb.net/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "tutor_db")


class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[DATABASE_NAME]
    
    def init_collections(self):
        """初始化集合"""
        # 创建必要的集合
        collections = [
            "users", "tutors", "tutor_details", "schools", "departments",
            "favorites", "bookings", "match_histories", "projects", 
            "project_applications", "score_lines"
        ]
        
        for collection in collections:
            if collection not in self.db.list_collection_names():
                self.db.create_collection(collection)
                print(f"创建集合: {collection}")
    
    def init_schools(self):
        """初始化学校数据"""
        schools = [
            {"id": "1", "name": "示例大学1", "location": "北京", "level": "985", "logo_url": "https://example.com/university1.png"},
            {"id": "2", "name": "示例大学2", "location": "上海", "level": "985", "logo_url": "https://example.com/university2.png"},
            {"id": "3", "name": "示例大学3", "location": "广州", "level": "211", "logo_url": "https://example.com/university3.png"},
        ]
        
        for school in schools:
            school["created_at"] = datetime.now()
            school["updated_at"] = datetime.now()
            self.db.schools.update_one(
                {"id": school["id"]},
                {"$set": school},
                upsert=True
            )
        
        print(f"初始化学校数据: {len(schools)} 条")
    
    def init_departments(self):
        """初始化院系数据"""
        departments = [
            {"id": "1", "school_id": "1", "name": "计算机科学与技术学院"},
            {"id": "2", "school_id": "1", "name": "信息科学技术学院"},
            {"id": "3", "school_id": "2", "name": "计算机学院"},
        ]
        
        for dept in departments:
            dept["created_at"] = datetime.now()
            dept["updated_at"] = datetime.now()
            self.db.departments.update_one(
                {"id": dept["id"]},
                {"$set": dept},
                upsert=True
            )
        
        print(f"初始化院系数据: {len(departments)} 条")
    
    def init_tutors(self):
        """初始化导师数据"""
        tutors = [
            {
                "id": "1",
                "name": "教师A",
                "title": "教授",
                "school_id": "1",
                "school_name": "示例大学1",
                "department_id": "1",
                "department_name": "计算机科学与技术学院",
                "bio": "教师A，博士生导师，主要研究方向为人工智能、机器学习。",
                "email": "teacherA@example.com",
                "phone": "13800000001",
                "avatar_url": "https://example.com/teacherA.jpg",
                "personal_page_url": "https://example.com/teacherA",
                "research_direction": "人工智能，机器学习，深度学习",
                "tags": ["AI", "机器学习", "深度学习"],
                "city": "北京",
                "crawled_at": datetime.now(),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": "2",
                "name": "教师B",
                "title": "副教授",
                "school_id": "2",
                "school_name": "示例大学2",
                "department_id": "3",
                "department_name": "计算机学院",
                "bio": "教师B，硕士生导师，主要研究方向为计算机视觉、图像处理。",
                "email": "teacherB@example.com",
                "phone": "13800000002",
                "avatar_url": "https://example.com/teacherB.jpg",
                "personal_page_url": "https://example.com/teacherB",
                "research_direction": "计算机视觉，图像处理，模式识别",
                "tags": ["计算机视觉", "图像处理"],
                "city": "上海",
                "crawled_at": datetime.now(),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        
        for tutor in tutors:
            self.db.tutors.update_one(
                {"id": tutor["id"]},
                {"$set": tutor},
                upsert=True
            )
        
        print(f"初始化导师数据: {len(tutors)} 条")
    
    def init_tutor_details(self):
        """初始化导师详细数据"""
        details = [
            {
                "tutor_id": "1",
                "bio": "教师A于2005年获得计算机科学博士学位，曾在国外知名大学做访问学者。主要研究人工智能和机器学习领域，发表论文多篇，主持国家级科研项目多项。",
                "achievements_summary": "发表SCI论文多篇，EI论文数十篇，授权专利多项。",
                "papers": [
                    {"title": "深度学习图像识别研究", "authors": ["教师A", "研究者B"], "journal": "计算机学报", "year": 2020},
                    {"title": "机器学习自然语言处理方法", "authors": ["教师A", "研究者C", "研究者D"], "journal": "软件学报", "year": 2019}
                ],
                "projects": [
                    {"title": "基于深度学习的智能图像处理研究", "funding": "国家自然科学基金", "start_date": "2018-01-01", "end_date": "2022-12-31"},
                    {"title": "人工智能应用研究", "funding": "省部级科研项目", "start_date": "2020-01-01", "end_date": "2023-12-31"}
                ],
                "coops": [
                    {"institution": "国外知名大学", "period": "2015-2016", "description": "访问学者合作研究"}
                ],
                "students": [
                    {"name": "学生A", "degree": "博士", "graduation_year": 2020, "current_position": "高校助理教授"},
                    {"name": "学生B", "degree": "硕士", "graduation_year": 2021, "current_position": "科技公司工程师"}
                ],
                "risks": [],
                "socials": [
                    {"platform": "github", "url": "https://github.com/teacherA"},
                    {"platform": "scholar", "url": "https://scholar.example.com/teacherA"}
                ]
            }
        ]
        
        for detail in details:
            self.db.tutor_details.update_one(
                {"tutor_id": detail["tutor_id"]},
                {"$set": detail},
                upsert=True
            )
        
        print(f"初始化导师详细数据: {len(details)} 条")
    
    def init_projects(self):
        """初始化项目数据"""
        projects = [
            {
                "id": "1",
                "title": "跨校AI研究合作项目",
                "type": "ai",
                "tags": ["人工智能", "跨校合作", "科研项目"],
                "description": "联合多所高校共同开展的人工智能基础研究项目，重点研究深度学习算法优化。",
                "requirements": "要求参与者具备扎实的机器学习基础，熟悉Python编程，有相关研究经验者优先。",
                "members": [
                    {"name": "教师A", "school": "示例大学1", "role": "项目负责人"},
                    {"name": "教师B", "school": "示例大学2", "role": "技术负责人"}
                ],
                "contact_info": "联系人：教师A，邮箱：teacherA@example.com",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        
        for project in projects:
            self.db.projects.update_one(
                {"id": project["id"]},
                {"$set": project},
                upsert=True
            )
        
        print(f"初始化项目数据: {len(projects)} 条")
    
    def init_score_lines(self):
        """初始化分数线数据"""
        score_lines = [
            {"id": "1", "school_id": "1", "department_id": "1", "year": 2023, "category": "计算机科学", "score": 380.5, "rank": 150},
            {"id": "2", "school_id": "1", "department_id": "1", "year": 2023, "category": "人工智能", "score": 385.0, "rank": 120},
        ]
        
        for score_line in score_lines:
            score_line["created_at"] = datetime.now()
            score_line["updated_at"] = datetime.now()
            self.db.score_lines.update_one(
                {"id": score_line["id"]},
                {"$set": score_line},
                upsert=True
            )
        
        print(f"初始化分数线数据: {len(score_lines)} 条")
    
    def run(self):
        """运行初始化"""
        print("开始初始化数据库...")
        
        try:
            self.init_collections()
            self.init_schools()
            self.init_departments()
            self.init_tutors()
            self.init_tutor_details()
            self.init_projects()
            self.init_score_lines()
            
            print("数据库初始化完成！")
            
        except Exception as e:
            print(f"数据库初始化失败: {str(e)}")
            raise
        
        finally:
            self.client.close()


if __name__ == "__main__":
    initializer = DatabaseInitializer()
    initializer.run()