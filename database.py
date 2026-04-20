from pymongo import MongoClient
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

class Database:
    def __init__(self, mongodb_uri='mongodb://localhost:27017/', db_name='medical_ai_db'):
        """Initialize database connection"""
        try:
            # MongoDB connection
            self.client = MongoClient(mongodb_uri)
            self.db = self.client[db_name]
            self.users = self.db['users']
            self.history = self.db['history']
            
            # Test connection
            self.client.server_info()
            print(f"✓ Connected to MongoDB: {db_name}")
        except Exception as e:
            print(f"✗ MongoDB connection failed: {str(e)}")
            print("  Please ensure MongoDB is running or check your connection string")
        
    def create_user(self, name, mobile, password):
        """Create a new user"""
        try:
            # Check if user already exists
            if self.users.find_one({'mobile': mobile}):
                return {'success': False, 'message': 'Mobile number already registered'}
            
            user_data = {
                'name': name,
                'mobile': mobile,
                'password': generate_password_hash(password),
                'created_at': datetime.now()
            }
            
            result = self.users.insert_one(user_data)
            return {'success': True, 'message': 'Account created successfully', 'user_id': str(result.inserted_id)}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def verify_user(self, mobile, password):
        """Verify user credentials"""
        try:
            user = self.users.find_one({'mobile': mobile})
            if user and check_password_hash(user['password'], password):
                return {
                    'success': True, 
                    'user_id': str(user['_id']),
                    'name': user['name'],
                    'mobile': user['mobile']
                }
            return {'success': False, 'message': 'Invalid credentials'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_user_by_mobile(self, mobile):
        """Get user by mobile number"""
        try:
            user = self.users.find_one({'mobile': mobile})
            if user:
                return {
                    'success': True,
                    'user_id': str(user['_id']),
                    'name': user['name'],
                    'mobile': user['mobile']
                }
            return {'success': False, 'message': 'User not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def update_password(self, mobile, new_password):
        """Update user password"""
        try:
            result = self.users.update_one(
                {'mobile': mobile},
                {'$set': {'password': generate_password_hash(new_password)}}
            )
            if result.modified_count > 0:
                return {'success': True, 'message': 'Password updated successfully'}
            return {'success': False, 'message': 'User not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def save_history(self, user_id, task_type, file_name, input_data, ai_output, language):
        """Save processing history"""
        try:
            history_data = {
                'user_id': user_id,
                'task_type': task_type,
                'file_name': file_name,
                'input_data': input_data,
                'ai_output': ai_output,
                'language': language,
                'date_time': datetime.now()
            }
            
            result = self.history.insert_one(history_data)
            return {'success': True, 'history_id': str(result.inserted_id)}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_user_history(self, user_id, limit=10):
        """Get user's processing history"""
        try:
            history_list = list(self.history.find({'user_id': user_id})
                              .sort('date_time', -1)
                              .limit(limit))
            
            # Convert ObjectId to string for JSON serialization
            for item in history_list:
                item['_id'] = str(item['_id'])
                item['date_time'] = item['date_time'].strftime('%Y-%m-%d %H:%M:%S')
            
            return {'success': True, 'history': history_list}
        except Exception as e:
            return {'success': False, 'message': str(e)}