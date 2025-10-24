# 🔍 Admin Preview Debug Guide

## How to Access and Test Admin Preview

### 1. **Access the Admin Panel**
- Go to: https://solana-rfp-tool.vercel.app/admin
- Login with the demo account
- You should see two tabs: "Knowledge Base Preview" and "Manage Entries"

### 2. **Test Admin Preview API Directly**
- Go to: https://solana-rfp-tool.vercel.app/test-admin
- This will test the admin preview API and show you exactly what data is being returned
- You should see 49 total entries with pagination

### 3. **Check Browser Console**
- Open browser developer tools (F12)
- Go to Console tab
- Look for any JavaScript errors when loading the admin page
- Check Network tab for failed API calls

### 4. **Verify API Endpoint**
The admin preview API should return:
```json
{
  "entries": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_entries": 49,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  },
  "filters": {
    "category": null,
    "search": null
  }
}
```

### 5. **Troubleshooting Steps**

#### If you see "No entries found":
1. Check if you're logged in properly
2. Verify the API URL is correct
3. Check browser console for errors

#### If the page loads but shows empty:
1. Check Network tab in browser dev tools
2. Look for failed API calls to `/api/v1/knowledge/admin/preview`
3. Check if the authorization token is being sent

#### If you see loading spinner forever:
1. Check browser console for JavaScript errors
2. Verify the API endpoint is accessible
3. Check if CORS is properly configured

### 6. **Expected Behavior**
- **Knowledge Base Preview tab**: Shows all 49 entries with pagination
- **Search functionality**: Filter entries by text
- **Category filter**: Filter by category (MXNB Q&A Pairs, etc.)
- **Pagination**: Navigate through pages of entries
- **Entry details**: Question, answer preview, category, tags, creation date

### 7. **Current Knowledge Base Status**
- ✅ **49 total entries** in knowledge base
- ✅ **22 entries fixed** with correct MXNB answers
- ✅ **API working** - returns proper data
- ✅ **Backend deployed** and accessible

### 8. **Quick Test Commands**
```bash
# Test API directly
curl -X GET "https://solana-rfp-271974794838.herokuapp.com/api/v1/knowledge/admin/preview?page=1&page_size=5" \
  -H "Authorization: Bearer mock-jwt-token-demo"

# Test frontend
curl -X GET "https://solana-rfp-tool.vercel.app/test-admin"
```

### 9. **If Still Not Working**
1. **Clear browser cache** and try again
2. **Try incognito/private mode**
3. **Check if Vercel deployment is up to date**
4. **Verify environment variables** are set correctly

The admin preview should now be working with all 49 entries visible!

