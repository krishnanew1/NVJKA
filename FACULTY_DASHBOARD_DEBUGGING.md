# Faculty Dashboard Debugging Guide

## Debug Logs Added

The Faculty Dashboard now includes comprehensive console logging to help identify data mismatch issues.

## Console Logs to Check

### 1. Component Mount Logs
```
🚀 FacultyDashboard mounted
👤 Current user from localStorage: {...}
🔑 Auth token exists: true/false
```

### 2. API Request Logs
```
🔍 Fetching faculty subjects from: /api/academics/faculty/my-subjects/
```

### 3. API Response Logs
```
📡 API Response: {status: 200, data: [...], ...}
📦 Response Data: [...]
📊 Data Type: object/array
📋 Is Array: true/false
```

### 4. Data Extraction Logs
```
✓ Paginated response detected
  OR
✓ Direct array response detected
  OR
⚠️ Unexpected response format: {...}
```

### 5. Extracted Data Logs
```
📚 Extracted Data: [...]
🔢 Number of subjects: X
📖 First subject: {...}
```

### 6. Error Logs
```
❌ Error fetching assignments: Error {...}
❌ Error response: {...}
❌ Error status: 404/401/403/500
❌ Error data: {...}
```

### 7. Completion Logs
```
✅ Fetch complete. Loading: false
```

## Debug Panel (Development Only)

In development mode, a debug panel appears showing:
```
🐛 Debug Info:
Assignments: X
Type: object/array
Is Array: Yes/No
```

## How to Debug

### Step 1: Open Browser Console
1. Open the Faculty Dashboard page
2. Press F12 or right-click → Inspect
3. Go to the Console tab

### Step 2: Check Mount Logs
Look for:
```
🚀 FacultyDashboard mounted
```

**If missing:** Component didn't mount - check routing

**If present:** Check the next logs

### Step 3: Check Auth Token
Look for:
```
🔑 Auth token exists: true
```

**If false:** User not logged in properly
- Check localStorage for `access_token`
- Try logging in again

**If true:** Token exists, continue

### Step 4: Check API Request
Look for:
```
🔍 Fetching faculty subjects from: /api/academics/faculty/my-subjects/
```

**If missing:** fetchAssignments() not called
- Check useEffect dependencies

**If present:** Request was made, check response

### Step 5: Check API Response
Look for:
```
📡 API Response: {...}
📦 Response Data: [...]
```

**Common Issues:**

**Issue 1: 404 Error**
```
❌ Error status: 404
```
**Solution:** Backend endpoint not found
- Check if backend server is running
- Verify URL: `/api/academics/faculty/my-subjects/`
- Check `backend/apps/academics/urls.py`

**Issue 2: 401 Error**
```
❌ Error status: 401
```
**Solution:** Authentication failed
- Token expired - log in again
- Token not sent - check `api.js` interceptor
- Token invalid - clear localStorage and log in

**Issue 3: 403 Error**
```
❌ Error status: 403
```
**Solution:** Access denied
- User doesn't have faculty role
- Check user role in database
- Verify FacultyProfile exists

**Issue 4: Empty Array**
```
📚 Extracted Data: []
🔢 Number of subjects: 0
```
**Solution:** No subjects assigned
- Check database: `Subject.objects.filter(faculty__user=user)`
- Assign subjects via Admin Faculty page
- Run `python manage.py seed_real_data` if needed

**Issue 5: Unexpected Format**
```
⚠️ Unexpected response format: {...}
```
**Solution:** Response structure changed
- Check what's in the response
- Update data extraction logic
- Verify serializer output

### Step 6: Check Data Extraction
Look for:
```
✓ Direct array response detected
📚 Extracted Data: [...]
🔢 Number of subjects: 2
```

**If number is 0:** No subjects assigned (see Issue 4 above)

**If number > 0:** Data extracted successfully, check rendering

### Step 7: Check First Subject
Look for:
```
📖 First subject: {
  id: 1,
  name: "Multivariate Data Analysis",
  code: "CS401",
  course: {...},
  semester: 4,
  ...
}
```

**Verify fields exist:**
- ✅ `id` - Required for key prop
- ✅ `name` - Displayed in card
- ✅ `code` - Displayed in card
- ✅ `course.name` - Displayed in card
- ✅ `semester` - Used for badge
- ✅ `semester_display` - Preferred for badge
- ✅ `credits` - Displayed in card

**If fields missing:** Serializer issue
- Check `SubjectSerializer` in backend
- Verify `select_related` includes course

## Common Scenarios

### Scenario 1: "No subjects assigned yet" message
**Possible Causes:**
1. `assignments` is empty array `[]`
2. No subjects assigned in database
3. Wrong faculty user logged in

**Debug Steps:**
1. Check console: `🔢 Number of subjects: 0`
2. Check database: `python backend/test_faculty_subjects_direct.py`
3. Verify logged-in user: Check `👤 Current user` log
4. Assign subjects via Admin Faculty page

### Scenario 2: Loading spinner never stops
**Possible Causes:**
1. API request hanging
2. Error not caught
3. `setLoading(false)` not called

**Debug Steps:**
1. Check console for error logs
2. Check Network tab for request status
3. Verify `finally` block executes
4. Check backend server is running

### Scenario 3: Cards render but data is wrong
**Possible Causes:**
1. Data structure mismatch
2. Wrong fields accessed
3. Null/undefined values

**Debug Steps:**
1. Check `📖 First subject` log
2. Compare with JSX field access
3. Add null checks: `subject.course?.name`
4. Use fallbacks: `subject.name || 'Unnamed'`

### Scenario 4: Console shows data but UI shows empty
**Possible Causes:**
1. State not updating
2. Re-render not triggered
3. Conditional rendering issue

**Debug Steps:**
1. Check `assignments` state in React DevTools
2. Verify `setAssignments()` called
3. Check conditional: `assignments && assignments.length > 0`
4. Look for JavaScript errors in console

## Testing Checklist

### Backend Tests
```bash
cd backend
python test_faculty_subjects_direct.py
```

**Expected Output:**
```
✓ Found faculty: Anuraj Singh
📚 Assigned Subjects: 2
  1. Python Programming Demo (CS101D)
  2. Advanced Numerical Methods (CS402)
```

### Frontend Tests

**Test 1: Login as Faculty**
1. Go to login page
2. Enter: `anuraj_s` / `faculty123`
3. Click Login
4. Should redirect to Faculty Dashboard

**Test 2: Check Console Logs**
1. Open Console (F12)
2. Look for mount logs
3. Look for API request logs
4. Look for response logs
5. Look for data extraction logs

**Test 3: Check Debug Panel**
1. Look for debug panel (development only)
2. Verify:
   - Assignments: 2 (or expected number)
   - Type: object
   - Is Array: Yes

**Test 4: Check UI**
1. Should see subject cards
2. Each card should show:
   - Subject name
   - Subject code
   - Course name
   - Semester badge
   - Credits
   - Two buttons

## Quick Fixes

### Fix 1: Clear Cache and Reload
```javascript
// In browser console
localStorage.clear();
location.reload();
```

### Fix 2: Re-login
1. Logout
2. Clear localStorage
3. Login again with faculty credentials

### Fix 3: Restart Backend
```bash
cd backend
python manage.py runserver
```

### Fix 4: Check Database
```bash
cd backend
python manage.py shell
```
```python
from apps.users.models import User, FacultyProfile
from apps.academics.models import Subject

# Check faculty exists
user = User.objects.get(username='anuraj_s')
faculty = FacultyProfile.objects.get(user=user)
print(f"Faculty: {faculty.user.get_full_name()}")

# Check subjects
subjects = Subject.objects.filter(faculty=faculty)
print(f"Subjects: {subjects.count()}")
for s in subjects:
    print(f"  - {s.name} ({s.code})")
```

### Fix 5: Assign Subjects
1. Login as admin
2. Go to Admin Faculty page
3. Find faculty member
4. Assign subjects using dropdowns
5. Click "Save Assignment"
6. Logout and login as faculty

## Expected Console Output (Success)

```
🚀 FacultyDashboard mounted
👤 Current user from localStorage: {"id":5,"username":"anuraj_s",...}
🔑 Auth token exists: true
🔍 Fetching faculty subjects from: /api/academics/faculty/my-subjects/
📡 API Response: {status: 200, data: Array(2), ...}
📦 Response Data: (2) [{...}, {...}]
📊 Data Type: object
📋 Is Array: true
✓ Direct array response detected
📚 Extracted Data: (2) [{...}, {...}]
🔢 Number of subjects: 2
📖 First subject: {id: 1, name: "Advanced Numerical Methods", code: "CS402", ...}
✅ Fetch complete. Loading: false
```

## Expected Console Output (Empty)

```
🚀 FacultyDashboard mounted
👤 Current user from localStorage: {"id":5,"username":"anuraj_s",...}
🔑 Auth token exists: true
🔍 Fetching faculty subjects from: /api/academics/faculty/my-subjects/
📡 API Response: {status: 200, data: Array(0), ...}
📦 Response Data: []
📊 Data Type: object
📋 Is Array: true
✓ Direct array response detected
📚 Extracted Data: []
🔢 Number of subjects: 0
✅ Fetch complete. Loading: false
```

## Expected Console Output (Error)

```
🚀 FacultyDashboard mounted
👤 Current user from localStorage: {"id":5,"username":"anuraj_s",...}
🔑 Auth token exists: true
🔍 Fetching faculty subjects from: /api/academics/faculty/my-subjects/
❌ Error fetching assignments: Error: Request failed with status code 404
❌ Error response: {status: 404, data: {...}}
❌ Error status: 404
❌ Error data: {detail: "Not found."}
ℹ️ 404 - Treating as empty state
✅ Fetch complete. Loading: false
```

## Support

If issues persist after following this guide:

1. **Copy all console logs** from browser
2. **Take screenshot** of UI
3. **Check backend logs** for errors
4. **Verify database** has subjects assigned
5. **Test with different faculty** accounts

---

**Created:** April 18, 2026
**Purpose:** Debug Faculty Dashboard data rendering issues
**Status:** Active debugging guide
