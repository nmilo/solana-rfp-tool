# AI Token Usage Management System

## Overview
A comprehensive system to monitor, control, and optimize AI token usage in the Solana RFP Database application.

## Key Features

### 1. **Usage Tracking & Analytics**
- Real-time token consumption monitoring
- Cost tracking per request/user/session
- Historical usage patterns and trends
- Token efficiency metrics

### 2. **Rate Limiting & Quotas**
- Per-user daily/monthly limits
- Request throttling
- Priority queues for different user types
- Emergency usage caps

### 3. **Cost Optimization**
- Response caching to reduce redundant API calls
- Smart question extraction (avoid unnecessary AI calls)
- Batch processing for multiple questions
- Model selection based on complexity

### 4. **Admin Controls**
- Usage dashboard with real-time metrics
- User quota management
- Cost alerts and notifications
- Usage reports and exports

## Implementation Plan

### Phase 1: Usage Tracking Database Schema

```sql
-- AI Usage Tracking
CREATE TABLE ai_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    request_type VARCHAR(50), -- 'pdf_extraction', 'question_enhancement'
    model_used VARCHAR(50), -- 'gpt-4', 'gpt-3.5-turbo'
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    cost_usd DECIMAL(10,6),
    processing_time_ms INTEGER,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Usage Quotas
CREATE TABLE user_quotas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) UNIQUE,
    daily_token_limit INTEGER DEFAULT 10000,
    monthly_token_limit INTEGER DEFAULT 100000,
    daily_cost_limit DECIMAL(10,2) DEFAULT 5.00,
    monthly_cost_limit DECIMAL(10,2) DEFAULT 50.00,
    current_daily_tokens INTEGER DEFAULT 0,
    current_monthly_tokens INTEGER DEFAULT 0,
    current_daily_cost DECIMAL(10,2) DEFAULT 0.00,
    current_monthly_cost DECIMAL(10,2) DEFAULT 0.00,
    last_reset_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Usage Statistics
CREATE TABLE usage_statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE,
    total_requests INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_cost DECIMAL(10,2) DEFAULT 0.00,
    unique_users INTEGER DEFAULT 0,
    avg_tokens_per_request DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Phase 2: Enhanced Backend Services

```python
# app/services/ai_usage_service.py
from typing import Dict, Optional, List
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.database import AIUsageLog, UserQuota, UsageStatistics
import openai

class AIUsageService:
    def __init__(self, db: Session):
        self.db = db
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Token costs (as of 2024)
        self.TOKEN_COSTS = {
            "gpt-4": {"input": 0.03/1000, "output": 0.06/1000},
            "gpt-4-turbo": {"input": 0.01/1000, "output": 0.03/1000},
            "gpt-3.5-turbo": {"input": 0.001/1000, "output": 0.002/1000}
        }
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage"""
        costs = self.TOKEN_COSTS.get(model, self.TOKEN_COSTS["gpt-4"])
        input_cost = input_tokens * costs["input"]
        output_cost = output_tokens * costs["output"]
        return input_cost + output_cost
    
    def log_usage(self, user_id: str, session_id: str, request_type: str, 
                  model: str, input_tokens: int, output_tokens: int, 
                  processing_time_ms: int, success: bool, error_message: str = None):
        """Log AI usage for tracking and billing"""
        
        total_tokens = input_tokens + output_tokens
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        
        usage_log = AIUsageLog(
            user_id=user_id,
            session_id=session_id,
            request_type=request_type,
            model_used=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            processing_time_ms=processing_time_ms,
            success=success,
            error_message=error_message
        )
        
        self.db.add(usage_log)
        
        # Update user quotas
        self.update_user_quotas(user_id, total_tokens, cost)
        
        # Update daily statistics
        self.update_daily_statistics(total_tokens, cost)
        
        self.db.commit()
    
    def check_quota(self, user_id: str) -> Dict[str, any]:
        """Check if user has remaining quota"""
        quota = self.db.query(UserQuota).filter(UserQuota.user_id == user_id).first()
        
        if not quota:
            # Create default quota for new user
            quota = UserQuota(user_id=user_id)
            self.db.add(quota)
            self.db.commit()
        
        # Reset daily counters if needed
        if quota.last_reset_date != date.today():
            quota.current_daily_tokens = 0
            quota.current_daily_cost = 0.00
            quota.last_reset_date = date.today()
            self.db.commit()
        
        return {
            "daily_tokens_remaining": quota.daily_token_limit - quota.current_daily_tokens,
            "monthly_tokens_remaining": quota.monthly_token_limit - quota.current_monthly_tokens,
            "daily_cost_remaining": quota.daily_cost_limit - quota.current_daily_cost,
            "monthly_cost_remaining": quota.monthly_cost_limit - quota.current_monthly_cost,
            "can_make_request": (
                quota.current_daily_tokens < quota.daily_token_limit and
                quota.current_monthly_tokens < quota.monthly_token_limit and
                quota.current_daily_cost < quota.daily_cost_limit and
                quota.current_monthly_cost < quota.monthly_cost_limit
            )
        }
    
    def get_usage_analytics(self, days: int = 30) -> Dict[str, any]:
        """Get usage analytics for dashboard"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Daily usage trends
        daily_usage = self.db.query(UsageStatistics).filter(
            UsageStatistics.date >= start_date,
            UsageStatistics.date <= end_date
        ).order_by(UsageStatistics.date).all()
        
        # Top users by usage
        top_users = self.db.query(
            AIUsageLog.user_id,
            func.sum(AIUsageLog.total_tokens).label('total_tokens'),
            func.sum(AIUsageLog.cost_usd).label('total_cost'),
            func.count(AIUsageLog.id).label('request_count')
        ).filter(
            AIUsageLog.created_at >= start_date
        ).group_by(AIUsageLog.user_id).order_by(
            func.sum(AIUsageLog.cost_usd).desc()
        ).limit(10).all()
        
        # Model usage breakdown
        model_usage = self.db.query(
            AIUsageLog.model_used,
            func.sum(AIUsageLog.total_tokens).label('total_tokens'),
            func.sum(AIUsageLog.cost_usd).label('total_cost'),
            func.count(AIUsageLog.id).label('request_count')
        ).filter(
            AIUsageLog.created_at >= start_date
        ).group_by(AIUsageLog.model_used).all()
        
        return {
            "daily_usage": [
                {
                    "date": str(stat.date),
                    "total_requests": stat.total_requests,
                    "total_tokens": stat.total_tokens,
                    "total_cost": float(stat.total_cost),
                    "unique_users": stat.unique_users
                }
                for stat in daily_usage
            ],
            "top_users": [
                {
                    "user_id": user.user_id,
                    "total_tokens": user.total_tokens,
                    "total_cost": float(user.total_cost),
                    "request_count": user.request_count
                }
                for user in top_users
            ],
            "model_usage": [
                {
                    "model": usage.model_used,
                    "total_tokens": usage.total_tokens,
                    "total_cost": float(usage.total_cost),
                    "request_count": usage.request_count
                }
                for usage in model_usage
            ]
        }
```

### Phase 3: Frontend Usage Dashboard

```tsx
// src/components/UsageDashboard.tsx
import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface UsageStats {
  daily_usage: Array<{
    date: string;
    total_requests: number;
    total_tokens: number;
    total_cost: number;
    unique_users: number;
  }>;
  top_users: Array<{
    user_id: string;
    total_tokens: number;
    total_cost: number;
    request_count: number;
  }>;
  model_usage: Array<{
    model: string;
    total_tokens: number;
    total_cost: number;
    request_count: number;
  }>;
}

export const UsageDashboard: React.FC = () => {
  const [stats, setStats] = useState<UsageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);

  useEffect(() => {
    loadUsageStats();
  }, [timeRange]);

  const loadUsageStats = async () => {
    try {
      const data = await apiService.getUsageAnalytics(timeRange);
      setStats(data);
    } catch (error) {
      console.error('Error loading usage stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-arena-accent"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="arena-card rounded-xl p-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-arena-text glow-text">
            AI Usage Dashboard
          </h1>
          <div className="flex space-x-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(Number(e.target.value))}
              className="arena-input px-4 py-2 rounded-lg"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="arena-card p-6 rounded-lg">
            <div className="text-arena-text-muted text-sm mb-2">Total Requests</div>
            <div className="text-3xl font-bold text-arena-text">
              {stats?.daily_usage.reduce((sum, day) => sum + day.total_requests, 0) || 0}
            </div>
          </div>
          <div className="arena-card p-6 rounded-lg">
            <div className="text-arena-text-muted text-sm mb-2">Total Tokens</div>
            <div className="text-3xl font-bold text-arena-accent">
              {stats?.daily_usage.reduce((sum, day) => sum + day.total_tokens, 0).toLocaleString() || 0}
            </div>
          </div>
          <div className="arena-card p-6 rounded-lg">
            <div className="text-arena-text-muted text-sm mb-2">Total Cost</div>
            <div className="text-3xl font-bold text-arena-success">
              ${stats?.daily_usage.reduce((sum, day) => sum + day.total_cost, 0).toFixed(2) || '0.00'}
            </div>
          </div>
          <div className="arena-card p-6 rounded-lg">
            <div className="text-arena-text-muted text-sm mb-2">Unique Users</div>
            <div className="text-3xl font-bold text-arena-warning">
              {Math.max(...(stats?.daily_usage.map(day => day.unique_users) || [0]))}
            </div>
          </div>
        </div>

        {/* Usage Chart */}
        <div className="arena-card p-6 rounded-lg mb-8">
          <h2 className="text-xl font-semibold text-arena-text mb-4">Daily Usage Trend</h2>
          <div className="h-64 flex items-end space-x-2">
            {stats?.daily_usage.map((day, index) => (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div
                  className="bg-arena-accent rounded-t w-full mb-2"
                  style={{ height: `${(day.total_cost / Math.max(...stats.daily_usage.map(d => d.total_cost))) * 200}px` }}
                ></div>
                <div className="text-xs text-arena-text-muted">
                  {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </div>
                <div className="text-xs text-arena-accent font-medium">
                  ${day.total_cost.toFixed(2)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Users and Model Usage */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Top Users */}
          <div className="arena-card p-6 rounded-lg">
            <h2 className="text-xl font-semibold text-arena-text mb-4">Top Users by Cost</h2>
            <div className="space-y-3">
              {stats?.top_users.map((user, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-arena-light-gray/30 rounded-lg">
                  <div>
                    <div className="font-medium text-arena-text">{user.user_id}</div>
                    <div className="text-sm text-arena-text-muted">
                      {user.request_count} requests • {user.total_tokens.toLocaleString()} tokens
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-arena-success">${user.total_cost.toFixed(2)}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Model Usage */}
          <div className="arena-card p-6 rounded-lg">
            <h2 className="text-xl font-semibold text-arena-text mb-4">Model Usage Breakdown</h2>
            <div className="space-y-3">
              {stats?.model_usage.map((model, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-arena-light-gray/30 rounded-lg">
                  <div>
                    <div className="font-medium text-arena-text">{model.model}</div>
                    <div className="text-sm text-arena-text-muted">
                      {model.request_count} requests • {model.total_tokens.toLocaleString()} tokens
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-arena-accent">${model.total_cost.toFixed(2)}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
```

### Phase 4: Cost Optimization Features

```python
# app/services/cache_service.py
import redis
import json
import hashlib
from typing import Optional, Dict, Any

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.cache_ttl = 3600  # 1 hour
    
    def get_cache_key(self, text: str, operation: str) -> str:
        """Generate cache key for text and operation"""
        content = f"{operation}:{text}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_response(self, text: str, operation: str) -> Optional[Dict[str, Any]]:
        """Get cached AI response"""
        cache_key = self.get_cache_key(text, operation)
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        return None
    
    def cache_response(self, text: str, operation: str, response: Dict[str, Any]):
        """Cache AI response"""
        cache_key = self.get_cache_key(text, operation)
        self.redis_client.setex(
            cache_key, 
            self.cache_ttl, 
            json.dumps(response)
        )
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        keys = self.redis_client.keys("*")
        return {
            "total_cached_items": len(keys),
            "cache_hit_rate": 0.0  # Would need to track hits/misses
        }
```

### Phase 5: Smart Question Processing

```python
# app/services/smart_processor.py
class SmartQuestionProcessor:
    def __init__(self, kb_service: KnowledgeBaseService, ai_service: AIService):
        self.kb_service = kb_service
        self.ai_service = ai_service
    
    async def process_questions_smart(self, text: str, user_id: str) -> Dict[str, Any]:
        """Smart processing that minimizes AI usage"""
        
        # Step 1: Try knowledge base first (no AI cost)
        questions = self.extract_questions_simple(text)
        kb_results = []
        
        for question in questions:
            best_match = self.kb_service.get_best_answer(question, min_confidence=0.3)
            if best_match and best_match["confidence"] > 0.7:
                # High confidence - no AI needed
                kb_results.append({
                    "question": question,
                    "answer": best_match["answer"],
                    "confidence": best_match["confidence"],
                    "source": "knowledge_base",
                    "ai_used": False
                })
            else:
                # Low confidence - might need AI enhancement
                kb_results.append({
                    "question": question,
                    "answer": best_match["answer"] if best_match else "No answer found",
                    "confidence": best_match["confidence"] if best_match else 0.0,
                    "source": "knowledge_base",
                    "ai_used": False,
                    "needs_ai_enhancement": True
                })
        
        # Step 2: Only use AI for low-confidence answers
        ai_enhanced_count = 0
        for result in kb_results:
            if result.get("needs_ai_enhancement") and result["confidence"] > 0.1:
                # Check quota before AI call
                quota_check = self.ai_service.check_quota(user_id)
                if not quota_check["can_make_request"]:
                    break
                
                # Use AI to enhance the answer
                enhanced = await self.ai_service.enhance_answer_with_context(
                    result["question"], 
                    result["answer"]
                )
                result["answer"] = enhanced["answer"]
                result["ai_used"] = True
                ai_enhanced_count += 1
        
        return {
            "questions_processed": len(questions),
            "answers_found": len([r for r in kb_results if r["confidence"] > 0]),
            "ai_enhanced": ai_enhanced_count,
            "total_ai_cost": ai_enhanced_count * 0.01,  # Estimated cost
            "results": kb_results
        }
```

## Implementation Benefits

### 1. **Cost Control**
- Real-time monitoring prevents budget overruns
- Quota system ensures fair usage
- Caching reduces redundant API calls

### 2. **Performance Optimization**
- Smart processing minimizes AI usage
- Batch operations reduce overhead
- Response caching improves speed

### 3. **User Experience**
- Transparent usage tracking
- Clear quota information
- Fast responses through caching

### 4. **Business Intelligence**
- Usage analytics for planning
- Cost optimization insights
- User behavior patterns

## Next Steps

1. **Implement database schema** for usage tracking
2. **Add Redis caching** for response optimization
3. **Build usage dashboard** for monitoring
4. **Create quota management** system
5. **Add cost alerts** and notifications

This system will give you complete control over AI token usage while maintaining excellent user experience and cost efficiency.
