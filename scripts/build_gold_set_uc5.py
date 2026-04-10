"""
build_gold_set_uc5.py
Builds the pre-registered 100-item gold set for UC5: Automated Code Review
Saves to: data/gold_sets/uc5_code_review.csv

Gold set structure:
  20 SECURITY items (SQL injection, XSS, command injection, hardcoded secrets, auth bypass)
  20 LOGIC_ERROR items (off-by-one, null access, wrong condition, infinite loop, race condition)
  20 PERFORMANCE items (N+1 queries, unnecessary allocation, blocking I/O, quadratic complexity)
  20 BEST_PRACTICE items (magic numbers, poor naming, missing error handling, tight coupling)
  20 CLEAN items (well-written, no issues)
  Each item: id, text, label, category, subcategory, difficulty, source, notes

PRE-REGISTRATION DATE: March 2, 2026
DO NOT MODIFY after benchmark execution begins.
"""

import csv
import os
import json
from datetime import datetime

# ── Output path ────────────────────────────────────────────────
OUTPUT_DIR  = "data/gold_sets"
OUTPUT_FILE = "uc5_code_review.csv"
META_FILE   = "uc5_metadata.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Gold set items ─────────────────────────────────────────────
# Columns: id, text, label, category, subcategory, difficulty, source, notes
# difficulty: easy / medium / hard
# source: synthetic
# Languages: Python, JavaScript, Java (mixed across categories)
# ──────────────────────────────────────────────────────────────

GOLD_SET = [

    # ══════════════════════════════════════════════════════════
    # SECURITY — 20 items (7 easy, 7 medium, 6 hard)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC5_001", "label": "SECURITY",
        "category": "SEC_Injection", "subcategory": "SQL Injection",
        "difficulty": "easy",
        "text": "def get_user(name):\n    query = \"SELECT * FROM users WHERE name = '\" + name + \"'\"\n    return db.execute(query)",
        "source": "synthetic",
        "notes": "Classic SQL injection via string concatenation — Python"
    },
    {
        "id": "UC5_002", "label": "SECURITY",
        "category": "SEC_Injection", "subcategory": "SQL Injection",
        "difficulty": "easy",
        "text": "app.get('/user', (req, res) => {\n    const q = `SELECT * FROM users WHERE id = ${req.query.id}`;\n    db.query(q, (err, rows) => res.json(rows));\n});",
        "source": "synthetic",
        "notes": "SQL injection via template literal — Node.js"
    },
    {
        "id": "UC5_003", "label": "SECURITY",
        "category": "SEC_Injection", "subcategory": "Command Injection",
        "difficulty": "easy",
        "text": "def ping_host(host):\n    import os\n    os.system('ping -c 1 ' + host)",
        "source": "synthetic",
        "notes": "OS command injection via os.system — Python"
    },
    {
        "id": "UC5_004", "label": "SECURITY",
        "category": "SEC_Secrets", "subcategory": "Hardcoded Secret",
        "difficulty": "easy",
        "text": "AWS_SECRET_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'\ns3 = boto3.client('s3', aws_secret_access_key=AWS_SECRET_KEY)",
        "source": "synthetic",
        "notes": "Hardcoded AWS secret key — Python"
    },
    {
        "id": "UC5_005", "label": "SECURITY",
        "category": "SEC_XSS", "subcategory": "Reflected XSS",
        "difficulty": "easy",
        "text": "app.get('/search', (req, res) => {\n    res.send(`<h1>Results for: ${req.query.q}</h1>`);\n});",
        "source": "synthetic",
        "notes": "Reflected XSS — unsanitized query param rendered in HTML — Node.js"
    },
    {
        "id": "UC5_006", "label": "SECURITY",
        "category": "SEC_Injection", "subcategory": "Code Injection",
        "difficulty": "easy",
        "text": "def calculate(expression):\n    return eval(expression)",
        "source": "synthetic",
        "notes": "Arbitrary code execution via eval on user input — Python"
    },
    {
        "id": "UC5_007", "label": "SECURITY",
        "category": "SEC_Secrets", "subcategory": "Hardcoded Secret",
        "difficulty": "easy",
        "text": "const jwt = require('jsonwebtoken');\nconst token = jwt.sign(payload, 'my-super-secret-key-123');",
        "source": "synthetic",
        "notes": "Hardcoded JWT signing secret — Node.js"
    },
    {
        "id": "UC5_008", "label": "SECURITY",
        "category": "SEC_Auth", "subcategory": "Auth Bypass",
        "difficulty": "medium",
        "text": "def is_admin(request):\n    return request.cookies.get('is_admin') == 'true'",
        "source": "synthetic",
        "notes": "Auth bypass — trusting client-side cookie for admin check — Python"
    },
    {
        "id": "UC5_009", "label": "SECURITY",
        "category": "SEC_Injection", "subcategory": "SQL Injection",
        "difficulty": "medium",
        "text": "String query = \"SELECT * FROM orders WHERE status = '\" + status\n    + \"' AND user_id = \" + userId;\nStatement stmt = conn.createStatement();\nResultSet rs = stmt.executeQuery(query);",
        "source": "synthetic",
        "notes": "SQL injection via Statement instead of PreparedStatement — Java"
    },
    {
        "id": "UC5_010", "label": "SECURITY",
        "category": "SEC_XSS", "subcategory": "Stored XSS",
        "difficulty": "medium",
        "text": "function Comment({ text }) {\n    return <div dangerouslySetInnerHTML={{ __html: text }} />;\n}",
        "source": "synthetic",
        "notes": "Stored XSS via dangerouslySetInnerHTML with user content — React"
    },
    {
        "id": "UC5_011", "label": "SECURITY",
        "category": "SEC_Injection", "subcategory": "Path Traversal",
        "difficulty": "medium",
        "text": "app.get('/file', (req, res) => {\n    const filepath = path.join('/uploads', req.query.name);\n    res.sendFile(filepath);\n});",
        "source": "synthetic",
        "notes": "Path traversal — user controls filename without sanitization — Node.js"
    },
    {
        "id": "UC5_012", "label": "SECURITY",
        "category": "SEC_Auth", "subcategory": "Insecure Comparison",
        "difficulty": "medium",
        "text": "def verify_token(user_token, real_token):\n    return user_token == real_token",
        "source": "synthetic",
        "notes": "Timing attack — should use hmac.compare_digest — Python"
    },
    {
        "id": "UC5_013", "label": "SECURITY",
        "category": "SEC_Injection", "subcategory": "SSRF",
        "difficulty": "medium",
        "text": "def fetch_url(url):\n    return requests.get(url).text\n\n@app.route('/proxy')\ndef proxy():\n    return fetch_url(request.args['url'])",
        "source": "synthetic",
        "notes": "SSRF — user-controlled URL with no validation — Flask"
    },
    {
        "id": "UC5_014", "label": "SECURITY",
        "category": "SEC_Secrets", "subcategory": "Hardcoded Credential",
        "difficulty": "medium",
        "text": "def get_db_connection():\n    return psycopg2.connect(\n        host='prod-db.internal', user='admin', password='Pr0d_p@ss!')",
        "source": "synthetic",
        "notes": "Hardcoded database credentials with production host — Python"
    },
    {
        "id": "UC5_015", "label": "SECURITY",
        "category": "SEC_Auth", "subcategory": "Mass Assignment",
        "difficulty": "hard",
        "text": "app.put('/profile', (req, res) => {\n    User.findByIdAndUpdate(req.user.id, req.body, { new: true })\n        .then(user => res.json(user));\n});",
        "source": "synthetic",
        "notes": "Mass assignment — entire req.body passed to update, user could set role — Node.js"
    },
    {
        "id": "UC5_016", "label": "SECURITY",
        "category": "SEC_Injection", "subcategory": "SQL Injection",
        "difficulty": "hard",
        "text": "def search_products(filters):\n    where_clauses = [f\"{k} = '{v}'\" for k, v in filters.items()]\n    query = 'SELECT * FROM products WHERE ' + ' AND '.join(where_clauses)\n    return db.execute(query)",
        "source": "synthetic",
        "notes": "SQL injection via dynamic filter construction — both keys and values injectable — Python"
    },
    {
        "id": "UC5_017", "label": "SECURITY",
        "category": "SEC_Auth", "subcategory": "IDOR",
        "difficulty": "hard",
        "text": "@app.route('/api/invoice/<invoice_id>')\n@login_required\ndef get_invoice(invoice_id):\n    invoice = Invoice.query.get(invoice_id)\n    return jsonify(invoice.to_dict())",
        "source": "synthetic",
        "notes": "IDOR — authenticated but no ownership check on invoice — Flask"
    },
    {
        "id": "UC5_018", "label": "SECURITY",
        "category": "SEC_Injection", "subcategory": "Deserialization",
        "difficulty": "hard",
        "text": "import pickle\n\ndef load_session(data):\n    return pickle.loads(base64.b64decode(data))",
        "source": "synthetic",
        "notes": "Insecure deserialization — pickle.loads on user-supplied data — Python"
    },
    {
        "id": "UC5_019", "label": "SECURITY",
        "category": "SEC_XSS", "subcategory": "DOM XSS",
        "difficulty": "hard",
        "text": "const name = new URLSearchParams(window.location.search).get('name');\ndocument.getElementById('greeting').innerHTML = 'Hello, ' + name;",
        "source": "synthetic",
        "notes": "DOM-based XSS via innerHTML with URL parameter — JavaScript"
    },
    {
        "id": "UC5_020", "label": "SECURITY",
        "category": "SEC_Auth", "subcategory": "JWT None Algorithm",
        "difficulty": "hard",
        "text": "const decoded = jwt.verify(token, SECRET, { algorithms: ['HS256', 'none'] });\nif (decoded.role === 'admin') grantAccess();",
        "source": "synthetic",
        "notes": "JWT 'none' algorithm allowed — attacker can forge unsigned tokens — Node.js"
    },

    # ══════════════════════════════════════════════════════════
    # LOGIC_ERROR — 20 items (7 easy, 7 medium, 6 hard)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC5_021", "label": "LOGIC_ERROR",
        "category": "LOGIC_Boundary", "subcategory": "Off By One",
        "difficulty": "easy",
        "text": "def get_last_n(items, n):\n    return items[len(items) - n - 1:]",
        "source": "synthetic",
        "notes": "Off-by-one — subtracts extra 1, returns n-1 items — Python"
    },
    {
        "id": "UC5_022", "label": "LOGIC_ERROR",
        "category": "LOGIC_Null", "subcategory": "Null Dereference",
        "difficulty": "easy",
        "text": "function getUserName(user) {\n    return user.profile.name;\n}",
        "source": "synthetic",
        "notes": "No null check — crashes if user or profile is null — JavaScript"
    },
    {
        "id": "UC5_023", "label": "LOGIC_ERROR",
        "category": "LOGIC_Condition", "subcategory": "Wrong Operator",
        "difficulty": "easy",
        "text": "def is_valid_age(age):\n    return age > 0 or age < 150",
        "source": "synthetic",
        "notes": "Should be 'and' not 'or' — condition is always True — Python"
    },
    {
        "id": "UC5_024", "label": "LOGIC_ERROR",
        "category": "LOGIC_Boundary", "subcategory": "Off By One",
        "difficulty": "easy",
        "text": "for (int i = 0; i <= arr.length; i++) {\n    System.out.println(arr[i]);\n}",
        "source": "synthetic",
        "notes": "Off-by-one — <= causes ArrayIndexOutOfBoundsException — Java"
    },
    {
        "id": "UC5_025", "label": "LOGIC_ERROR",
        "category": "LOGIC_Condition", "subcategory": "Wrong Condition",
        "difficulty": "easy",
        "text": "def find_max(numbers):\n    max_val = 0\n    for n in numbers:\n        if n > max_val:\n            max_val = n\n    return max_val",
        "source": "synthetic",
        "notes": "Fails for all-negative lists — initializes to 0 instead of float('-inf') — Python"
    },
    {
        "id": "UC5_026", "label": "LOGIC_ERROR",
        "category": "LOGIC_Loop", "subcategory": "Infinite Loop",
        "difficulty": "easy",
        "text": "let i = 10;\nwhile (i > 0) {\n    console.log(i);\n    i++;\n}",
        "source": "synthetic",
        "notes": "Infinite loop — increments instead of decrements — JavaScript"
    },
    {
        "id": "UC5_027", "label": "LOGIC_ERROR",
        "category": "LOGIC_Null", "subcategory": "Undefined Access",
        "difficulty": "easy",
        "text": "const config = JSON.parse(fs.readFileSync('config.json'));\nconsole.log(config.database.host.trim());",
        "source": "synthetic",
        "notes": "No check if database or host exists — TypeError on undefined — Node.js"
    },
    {
        "id": "UC5_028", "label": "LOGIC_ERROR",
        "category": "LOGIC_Condition", "subcategory": "Boolean Logic",
        "difficulty": "medium",
        "text": "def can_access(user):\n    if not user.is_active and user.is_verified:\n        return True\n    return False",
        "source": "synthetic",
        "notes": "Precedence bug — 'not' only applies to is_active, should be not (is_active and is_verified) or needs parens — Python"
    },
    {
        "id": "UC5_029", "label": "LOGIC_ERROR",
        "category": "LOGIC_Boundary", "subcategory": "Empty Collection",
        "difficulty": "medium",
        "text": "def average(scores):\n    return sum(scores) / len(scores)",
        "source": "synthetic",
        "notes": "ZeroDivisionError when scores is empty — Python"
    },
    {
        "id": "UC5_030", "label": "LOGIC_ERROR",
        "category": "LOGIC_Condition", "subcategory": "Type Coercion",
        "difficulty": "medium",
        "text": "function isEqual(a, b) {\n    return a == b;\n}\nconsole.log(isEqual('0', false));  // true",
        "source": "synthetic",
        "notes": "Type coercion bug — should use === for strict equality — JavaScript"
    },
    {
        "id": "UC5_031", "label": "LOGIC_ERROR",
        "category": "LOGIC_Null", "subcategory": "Optional Chaining Missing",
        "difficulty": "medium",
        "text": "Map<String, List<String>> groups = getGroups();\nint count = groups.get(key).size();",
        "source": "synthetic",
        "notes": "NullPointerException if key not in map — Java"
    },
    {
        "id": "UC5_032", "label": "LOGIC_ERROR",
        "category": "LOGIC_Loop", "subcategory": "Mutation During Iteration",
        "difficulty": "medium",
        "text": "def remove_negatives(numbers):\n    for n in numbers:\n        if n < 0:\n            numbers.remove(n)\n    return numbers",
        "source": "synthetic",
        "notes": "Modifying list during iteration — skips elements — Python"
    },
    {
        "id": "UC5_033", "label": "LOGIC_ERROR",
        "category": "LOGIC_Condition", "subcategory": "Short Circuit",
        "difficulty": "medium",
        "text": "function validate(input) {\n    if (input.length > 0 || input !== null) {\n        return process(input);\n    }\n}",
        "source": "synthetic",
        "notes": "Wrong order — checks length before null check, and should use && not || — JavaScript"
    },
    {
        "id": "UC5_034", "label": "LOGIC_ERROR",
        "category": "LOGIC_Boundary", "subcategory": "Fence Post",
        "difficulty": "medium",
        "text": "def count_days_between(start, end):\n    delta = end - start\n    return delta.days + 1",
        "source": "synthetic",
        "notes": "Fence-post error — off by one depending on inclusive/exclusive semantics — Python"
    },
    {
        "id": "UC5_035", "label": "LOGIC_ERROR",
        "category": "LOGIC_Race", "subcategory": "TOCTOU",
        "difficulty": "hard",
        "text": "def transfer(from_acct, to_acct, amount):\n    if from_acct.balance >= amount:\n        from_acct.balance -= amount\n        to_acct.balance += amount",
        "source": "synthetic",
        "notes": "TOCTOU race condition — no locking between check and update — Python"
    },
    {
        "id": "UC5_036", "label": "LOGIC_ERROR",
        "category": "LOGIC_Condition", "subcategory": "Mutable Default",
        "difficulty": "hard",
        "text": "def add_item(item, items=[]):\n    items.append(item)\n    return items",
        "source": "synthetic",
        "notes": "Mutable default argument — list persists across calls — Python"
    },
    {
        "id": "UC5_037", "label": "LOGIC_ERROR",
        "category": "LOGIC_Race", "subcategory": "Race Condition",
        "difficulty": "hard",
        "text": "let counter = 0;\nasync function incrementAll(ids) {\n    ids.forEach(async (id) => {\n        const val = await db.get(id);\n        await db.set(id, val + 1);\n        counter++;\n    });\n}",
        "source": "synthetic",
        "notes": "Race condition — concurrent async ops in forEach, counter not atomic — Node.js"
    },
    {
        "id": "UC5_038", "label": "LOGIC_ERROR",
        "category": "LOGIC_Condition", "subcategory": "Closure Bug",
        "difficulty": "hard",
        "text": "for (var i = 0; i < 5; i++) {\n    setTimeout(function() {\n        console.log(i);\n    }, 100);\n}",
        "source": "synthetic",
        "notes": "Closure over var — prints 5 five times instead of 0-4 — JavaScript"
    },
    {
        "id": "UC5_039", "label": "LOGIC_ERROR",
        "category": "LOGIC_Null", "subcategory": "Promise Rejection",
        "difficulty": "hard",
        "text": "async function loadData() {\n    const resp = await fetch('/api/data');\n    const data = await resp.json();\n    return data.results.map(r => r.name);\n}",
        "source": "synthetic",
        "notes": "No check on resp.ok, no try/catch, crashes if results is null — JavaScript"
    },
    {
        "id": "UC5_040", "label": "LOGIC_ERROR",
        "category": "LOGIC_Condition", "subcategory": "Float Comparison",
        "difficulty": "hard",
        "text": "def apply_discount(price, discount):\n    final = price - (price * discount)\n    if final == 29.99:\n        return 'Special offer!'\n    return f'${final:.2f}'",
        "source": "synthetic",
        "notes": "Floating point comparison — 29.990000000000002 != 29.99 — Python"
    },

    # ══════════════════════════════════════════════════════════
    # PERFORMANCE — 20 items (7 easy, 7 medium, 6 hard)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC5_041", "label": "PERFORMANCE",
        "category": "PERF_Complexity", "subcategory": "Quadratic",
        "difficulty": "easy",
        "text": "def has_duplicates(items):\n    for i in range(len(items)):\n        for j in range(len(items)):\n            if i != j and items[i] == items[j]:\n                return True\n    return False",
        "source": "synthetic",
        "notes": "O(n^2) duplicate check — should use set — Python"
    },
    {
        "id": "UC5_042", "label": "PERFORMANCE",
        "category": "PERF_Query", "subcategory": "N+1 Query",
        "difficulty": "easy",
        "text": "def get_order_details(orders):\n    result = []\n    for order in orders:\n        items = OrderItem.objects.filter(order_id=order.id)\n        result.append({'order': order, 'items': list(items)})\n    return result",
        "source": "synthetic",
        "notes": "N+1 query — should use select_related or prefetch_related — Django"
    },
    {
        "id": "UC5_043", "label": "PERFORMANCE",
        "category": "PERF_Allocation", "subcategory": "String Concatenation",
        "difficulty": "easy",
        "text": "def build_report(records):\n    output = ''\n    for r in records:\n        output += f'{r.name}: {r.value}\\n'\n    return output",
        "source": "synthetic",
        "notes": "String concatenation in loop — O(n^2) — should use join or list — Python"
    },
    {
        "id": "UC5_044", "label": "PERFORMANCE",
        "category": "PERF_Complexity", "subcategory": "Repeated Computation",
        "difficulty": "easy",
        "text": "function findCommon(arr1, arr2) {\n    return arr1.filter(item => arr2.includes(item));\n}",
        "source": "synthetic",
        "notes": "O(n*m) — arr2.includes is linear; should convert arr2 to Set — JavaScript"
    },
    {
        "id": "UC5_045", "label": "PERFORMANCE",
        "category": "PERF_Allocation", "subcategory": "Unnecessary Copy",
        "difficulty": "easy",
        "text": "def count_words(text):\n    words = list(text.split())\n    return len(words)",
        "source": "synthetic",
        "notes": "Unnecessary list() copy — split already returns a list — Python"
    },
    {
        "id": "UC5_046", "label": "PERFORMANCE",
        "category": "PERF_Query", "subcategory": "Select All",
        "difficulty": "easy",
        "text": "def get_user_email(user_id):\n    user = User.objects.filter(id=user_id).first()\n    return user.email if user else None",
        "source": "synthetic",
        "notes": "Fetches all columns when only email is needed — should use .values_list or .only — Django"
    },
    {
        "id": "UC5_047", "label": "PERFORMANCE",
        "category": "PERF_Complexity", "subcategory": "Repeated Lookup",
        "difficulty": "easy",
        "text": "def count_by_category(items):\n    categories = set(i.category for i in items)\n    return {c: len([i for i in items if i.category == c]) for c in categories}",
        "source": "synthetic",
        "notes": "O(n*k) — iterates full list per category; should use Counter or single pass — Python"
    },
    {
        "id": "UC5_048", "label": "PERFORMANCE",
        "category": "PERF_IO", "subcategory": "Blocking IO",
        "difficulty": "medium",
        "text": "app.get('/data', async (req, res) => {\n    const data = fs.readFileSync('/tmp/cache.json');\n    res.json(JSON.parse(data));\n});",
        "source": "synthetic",
        "notes": "Blocking readFileSync in async Express handler — blocks event loop — Node.js"
    },
    {
        "id": "UC5_049", "label": "PERFORMANCE",
        "category": "PERF_Query", "subcategory": "N+1 Query",
        "difficulty": "medium",
        "text": "const users = await User.findAll();\nfor (const user of users) {\n    user.posts = await Post.findAll({ where: { userId: user.id } });\n}",
        "source": "synthetic",
        "notes": "N+1 query — should use eager loading with include — Sequelize/Node.js"
    },
    {
        "id": "UC5_050", "label": "PERFORMANCE",
        "category": "PERF_Allocation", "subcategory": "Memory Waste",
        "difficulty": "medium",
        "text": "def process_large_file(path):\n    data = open(path).read()\n    for line in data.split('\\n'):\n        process(line)",
        "source": "synthetic",
        "notes": "Reads entire file into memory — should iterate line by line — Python"
    },
    {
        "id": "UC5_051", "label": "PERFORMANCE",
        "category": "PERF_Complexity", "subcategory": "Unnecessary Sort",
        "difficulty": "medium",
        "text": "def get_top_score(scores):\n    sorted_scores = sorted(scores, reverse=True)\n    return sorted_scores[0]",
        "source": "synthetic",
        "notes": "O(n log n) sort to find max — should use max() which is O(n) — Python"
    },
    {
        "id": "UC5_052", "label": "PERFORMANCE",
        "category": "PERF_Query", "subcategory": "Missing Index",
        "difficulty": "medium",
        "text": "def find_recent_orders(email):\n    return Order.objects.filter(\n        customer_email=email,\n        created_at__gte=datetime.now() - timedelta(days=30)\n    ).order_by('-created_at')",
        "source": "synthetic",
        "notes": "Filter + sort on unindexed fields — full table scan on large table — Django"
    },
    {
        "id": "UC5_053", "label": "PERFORMANCE",
        "category": "PERF_Allocation", "subcategory": "Regex Recompile",
        "difficulty": "medium",
        "text": "def extract_emails(texts):\n    results = []\n    for text in texts:\n        matches = re.findall(r'[\\w.]+@[\\w.]+', text)\n        results.extend(matches)\n    return results",
        "source": "synthetic",
        "notes": "Regex recompiled every iteration — should compile once outside loop — Python"
    },
    {
        "id": "UC5_054", "label": "PERFORMANCE",
        "category": "PERF_IO", "subcategory": "Sequential Awaits",
        "difficulty": "medium",
        "text": "async function loadDashboard(userId) {\n    const profile = await fetchProfile(userId);\n    const orders = await fetchOrders(userId);\n    const notifications = await fetchNotifications(userId);\n    return { profile, orders, notifications };\n}",
        "source": "synthetic",
        "notes": "Sequential awaits — three independent requests should use Promise.all — JavaScript"
    },
    {
        "id": "UC5_055", "label": "PERFORMANCE",
        "category": "PERF_Complexity", "subcategory": "Quadratic",
        "difficulty": "hard",
        "text": "public List<String> removeDuplicates(List<String> input) {\n    List<String> result = new ArrayList<>();\n    for (String s : input) {\n        if (!result.contains(s)) result.add(s);\n    }\n    return result;\n}",
        "source": "synthetic",
        "notes": "O(n^2) — ArrayList.contains is O(n); should use LinkedHashSet — Java"
    },
    {
        "id": "UC5_056", "label": "PERFORMANCE",
        "category": "PERF_IO", "subcategory": "Unbatched Writes",
        "difficulty": "hard",
        "text": "async function saveAll(records) {\n    for (const record of records) {\n        await db.collection('items').insertOne(record);\n    }\n}",
        "source": "synthetic",
        "notes": "Unbatched inserts — should use insertMany for bulk operation — MongoDB/Node.js"
    },
    {
        "id": "UC5_057", "label": "PERFORMANCE",
        "category": "PERF_Allocation", "subcategory": "Cartesian Join",
        "difficulty": "hard",
        "text": "def match_pairs(list_a, list_b):\n    pairs = [(a, b) for a in list_a for b in list_b if a.key == b.key]\n    return pairs",
        "source": "synthetic",
        "notes": "O(n*m) nested comprehension — should use dict lookup for O(n+m) — Python"
    },
    {
        "id": "UC5_058", "label": "PERFORMANCE",
        "category": "PERF_Complexity", "subcategory": "Exponential Recursion",
        "difficulty": "hard",
        "text": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n - 1) + fibonacci(n - 2)",
        "source": "synthetic",
        "notes": "O(2^n) naive recursion — should use memoization or iterative — Python"
    },
    {
        "id": "UC5_059", "label": "PERFORMANCE",
        "category": "PERF_IO", "subcategory": "Blocking IO",
        "difficulty": "hard",
        "text": "public String fetchAllData(List<String> urls) throws Exception {\n    StringBuilder sb = new StringBuilder();\n    for (String url : urls) {\n        HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();\n        sb.append(new String(conn.getInputStream().readAllBytes()));\n    }\n    return sb.toString();\n}",
        "source": "synthetic",
        "notes": "Sequential blocking HTTP calls — should use CompletableFuture or virtual threads — Java"
    },
    {
        "id": "UC5_060", "label": "PERFORMANCE",
        "category": "PERF_Query", "subcategory": "Over Fetching",
        "difficulty": "hard",
        "text": "def export_report():\n    users = User.objects.all()\n    return [{'name': u.name, 'email': u.email} for u in users]",
        "source": "synthetic",
        "notes": "Loads all model fields + all rows into memory; should use .only().iterator() — Django"
    },

    # ══════════════════════════════════════════════════════════
    # BEST_PRACTICE — 20 items (7 easy, 7 medium, 6 hard)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC5_061", "label": "BEST_PRACTICE",
        "category": "BP_Naming", "subcategory": "Poor Naming",
        "difficulty": "easy",
        "text": "def f(x, y):\n    return x * y * 0.0825",
        "source": "synthetic",
        "notes": "Poor naming — f, x, y meaningless; 0.0825 is a magic number (tax rate) — Python"
    },
    {
        "id": "UC5_062", "label": "BEST_PRACTICE",
        "category": "BP_Magic", "subcategory": "Magic Number",
        "difficulty": "easy",
        "text": "if (response.status === 422) {\n    showError('Validation failed');\n} else if (response.status === 429) {\n    retry();\n}",
        "source": "synthetic",
        "notes": "Magic numbers — HTTP status codes should be named constants — JavaScript"
    },
    {
        "id": "UC5_063", "label": "BEST_PRACTICE",
        "category": "BP_ErrorHandling", "subcategory": "Bare Except",
        "difficulty": "easy",
        "text": "try:\n    process_payment(order)\nexcept:\n    pass",
        "source": "synthetic",
        "notes": "Bare except with pass — silently swallows all errors including SystemExit — Python"
    },
    {
        "id": "UC5_064", "label": "BEST_PRACTICE",
        "category": "BP_ErrorHandling", "subcategory": "Empty Catch",
        "difficulty": "easy",
        "text": "try {\n    connection.close();\n} catch (SQLException e) {\n    // TODO: handle this\n}",
        "source": "synthetic",
        "notes": "Empty catch block — silently ignores SQL errors — Java"
    },
    {
        "id": "UC5_065", "label": "BEST_PRACTICE",
        "category": "BP_Naming", "subcategory": "Misleading Name",
        "difficulty": "easy",
        "text": "def get_users():\n    users = User.objects.all()\n    for u in users:\n        u.last_login = datetime.now()\n        u.save()\n    return users",
        "source": "synthetic",
        "notes": "Misleading name — get_users has side effect of updating last_login — Django"
    },
    {
        "id": "UC5_066", "label": "BEST_PRACTICE",
        "category": "BP_Validation", "subcategory": "No Input Validation",
        "difficulty": "easy",
        "text": "app.post('/register', (req, res) => {\n    const { email, password } = req.body;\n    User.create({ email, password });\n    res.status(201).send('Created');\n});",
        "source": "synthetic",
        "notes": "No input validation — no email format check, no password strength check — Node.js"
    },
    {
        "id": "UC5_067", "label": "BEST_PRACTICE",
        "category": "BP_Magic", "subcategory": "Magic String",
        "difficulty": "easy",
        "text": "def process_order(order):\n    if order.status == 'pndg':\n        order.status = 'proc'\n    elif order.status == 'proc':\n        order.status = 'shpd'",
        "source": "synthetic",
        "notes": "Magic strings with unclear abbreviations — should use enum or constants — Python"
    },
    {
        "id": "UC5_068", "label": "BEST_PRACTICE",
        "category": "BP_Coupling", "subcategory": "Tight Coupling",
        "difficulty": "medium",
        "text": "class OrderService {\n    process(order) {\n        const tax = order.items.reduce((s, i) => s + i.price * 0.08, 0);\n        new EmailService().send(order.email, `Total: $${order.total + tax}`);\n        new InventoryDB().decrement(order.items);\n    }\n}",
        "source": "synthetic",
        "notes": "Tight coupling — directly instantiates EmailService and InventoryDB — JavaScript"
    },
    {
        "id": "UC5_069", "label": "BEST_PRACTICE",
        "category": "BP_ErrorHandling", "subcategory": "Broad Exception",
        "difficulty": "medium",
        "text": "def parse_config(path):\n    try:\n        with open(path) as f:\n            return json.load(f)\n    except Exception as e:\n        return {}",
        "source": "synthetic",
        "notes": "Catches Exception too broadly — hides FileNotFoundError vs JSONDecodeError — Python"
    },
    {
        "id": "UC5_070", "label": "BEST_PRACTICE",
        "category": "BP_Validation", "subcategory": "No Return Validation",
        "difficulty": "medium",
        "text": "public void updatePrice(int productId, double newPrice) {\n    Product p = productRepo.findById(productId).orElse(null);\n    p.setPrice(newPrice);\n    productRepo.save(p);\n}",
        "source": "synthetic",
        "notes": "No null check after orElse(null) — NullPointerException if product missing — Java"
    },
    {
        "id": "UC5_071", "label": "BEST_PRACTICE",
        "category": "BP_Naming", "subcategory": "Boolean Naming",
        "difficulty": "medium",
        "text": "const data = checkPermission(user, resource);\nif (!data) {\n    throw new Error('Forbidden');\n}",
        "source": "synthetic",
        "notes": "Poor naming — 'data' for a boolean return, 'check' should be 'has' or 'can' — JavaScript"
    },
    {
        "id": "UC5_072", "label": "BEST_PRACTICE",
        "category": "BP_Coupling", "subcategory": "God Function",
        "difficulty": "medium",
        "text": "def handle_request(request):\n    validate(request)\n    user = authenticate(request)\n    data = fetch_data(user)\n    transformed = transform(data)\n    result = compute(transformed)\n    cache_result(result)\n    log_request(request, result)\n    return format_response(result)",
        "source": "synthetic",
        "notes": "God function — orchestrates too many concerns; violates SRP — Python"
    },
    {
        "id": "UC5_073", "label": "BEST_PRACTICE",
        "category": "BP_Magic", "subcategory": "Magic Number",
        "difficulty": "medium",
        "text": "def calculate_shipping(weight):\n    if weight < 5:\n        return 4.99\n    elif weight < 20:\n        return 9.99\n    else:\n        return 14.99 + (weight - 20) * 0.50",
        "source": "synthetic",
        "notes": "Multiple magic numbers for weight thresholds and prices — Python"
    },
    {
        "id": "UC5_074", "label": "BEST_PRACTICE",
        "category": "BP_ErrorHandling", "subcategory": "Missing Finally",
        "difficulty": "medium",
        "text": "Connection conn = DriverManager.getConnection(url);\ntry {\n    Statement stmt = conn.createStatement();\n    ResultSet rs = stmt.executeQuery(sql);\n    return processResults(rs);\n} catch (SQLException e) {\n    logger.error(e);\n    return null;\n}",
        "source": "synthetic",
        "notes": "Connection never closed — missing finally or try-with-resources — Java"
    },
    {
        "id": "UC5_075", "label": "BEST_PRACTICE",
        "category": "BP_Validation", "subcategory": "Truthy Checking",
        "difficulty": "hard",
        "text": "function processAge(age) {\n    if (age) {\n        return `Age: ${age}`;\n    }\n    return 'Unknown';\n}",
        "source": "synthetic",
        "notes": "Truthy check fails for age=0 which is a valid age — should check !== undefined — JavaScript"
    },
    {
        "id": "UC5_076", "label": "BEST_PRACTICE",
        "category": "BP_Coupling", "subcategory": "Leaky Abstraction",
        "difficulty": "hard",
        "text": "class UserRepository:\n    def get_active_users(self):\n        return User.objects.raw(\n            'SELECT * FROM auth_user WHERE is_active = 1 AND last_login > NOW() - INTERVAL 30 DAY')",
        "source": "synthetic",
        "notes": "Raw SQL in repository — leaks DB dialect, breaks portability, bypasses ORM — Django"
    },
    {
        "id": "UC5_077", "label": "BEST_PRACTICE",
        "category": "BP_ErrorHandling", "subcategory": "Swallowed Error",
        "difficulty": "hard",
        "text": "async function saveUser(user) {\n    try {\n        await db.users.insert(user);\n        return { success: true };\n    } catch (e) {\n        console.log('save failed');\n        return { success: false };\n    }\n}",
        "source": "synthetic",
        "notes": "Swallows error details — caller cannot distinguish duplicate key vs connection failure — Node.js"
    },
    {
        "id": "UC5_078", "label": "BEST_PRACTICE",
        "category": "BP_Naming", "subcategory": "Inconsistent Convention",
        "difficulty": "hard",
        "text": "class DataProcessor:\n    def fetchData(self): ...\n    def process_data(self): ...\n    def SaveResults(self): ...\n    def CLEANUP(self): ...",
        "source": "synthetic",
        "notes": "Four different naming conventions in one class — camelCase, snake_case, PascalCase, UPPER — Python"
    },
    {
        "id": "UC5_079", "label": "BEST_PRACTICE",
        "category": "BP_Coupling", "subcategory": "Feature Envy",
        "difficulty": "hard",
        "text": "def calculate_total(cart):\n    subtotal = sum(item.price * item.qty for item in cart.items)\n    tax = subtotal * cart.tax_rate\n    discount = subtotal * cart.discount_pct\n    shipping = 5.99 if subtotal < cart.free_ship_min else 0\n    return subtotal + tax - discount + shipping",
        "source": "synthetic",
        "notes": "Feature envy — function accesses too many cart internals; should be a method on Cart — Python"
    },
    {
        "id": "UC5_080", "label": "BEST_PRACTICE",
        "category": "BP_Validation", "subcategory": "Missing Boundary Check",
        "difficulty": "hard",
        "text": "public void setDiscount(double percent) {\n    this.discount = percent;\n    this.finalPrice = this.basePrice * (1 - percent / 100);\n}",
        "source": "synthetic",
        "notes": "No boundary validation — negative percent or >100 produces nonsensical prices — Java"
    },

    # ══════════════════════════════════════════════════════════
    # CLEAN — 20 items (7 easy, 7 medium, 6 hard)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC5_081", "label": "CLEAN",
        "category": "CLEAN_Pythonic", "subcategory": "Simple Function",
        "difficulty": "easy",
        "text": "def is_palindrome(s: str) -> bool:\n    cleaned = s.lower().strip()\n    return cleaned == cleaned[::-1]",
        "source": "synthetic",
        "notes": "Clean — simple, well-named, type-hinted palindrome check — Python"
    },
    {
        "id": "UC5_082", "label": "CLEAN",
        "category": "CLEAN_JS", "subcategory": "Array Operation",
        "difficulty": "easy",
        "text": "const getActiveEmails = (users) =>\n    users.filter(u => u.isActive).map(u => u.email);",
        "source": "synthetic",
        "notes": "Clean — concise functional chain, descriptive name — JavaScript"
    },
    {
        "id": "UC5_083", "label": "CLEAN",
        "category": "CLEAN_Java", "subcategory": "Null Safety",
        "difficulty": "easy",
        "text": "public Optional<User> findByEmail(String email) {\n    return Optional.ofNullable(userMap.get(email));\n}",
        "source": "synthetic",
        "notes": "Clean — uses Optional correctly, clear naming — Java"
    },
    {
        "id": "UC5_084", "label": "CLEAN",
        "category": "CLEAN_Pythonic", "subcategory": "Context Manager",
        "difficulty": "easy",
        "text": "def read_config(path: str) -> dict:\n    with open(path, 'r') as f:\n        return json.load(f)",
        "source": "synthetic",
        "notes": "Clean — proper context manager, type hints, simple — Python"
    },
    {
        "id": "UC5_085", "label": "CLEAN",
        "category": "CLEAN_JS", "subcategory": "Destructuring",
        "difficulty": "easy",
        "text": "const formatUser = ({ name, email, role }) => ({\n    displayName: name,\n    contact: email,\n    isAdmin: role === 'admin',\n});",
        "source": "synthetic",
        "notes": "Clean — destructuring, clear naming, pure function — JavaScript"
    },
    {
        "id": "UC5_086", "label": "CLEAN",
        "category": "CLEAN_Pythonic", "subcategory": "List Comprehension",
        "difficulty": "easy",
        "text": "def get_even_squares(numbers: list[int]) -> list[int]:\n    return [n ** 2 for n in numbers if n % 2 == 0]",
        "source": "synthetic",
        "notes": "Clean — idiomatic list comprehension, typed, readable — Python"
    },
    {
        "id": "UC5_087", "label": "CLEAN",
        "category": "CLEAN_Java", "subcategory": "Stream API",
        "difficulty": "easy",
        "text": "public List<String> getActiveUserNames(List<User> users) {\n    return users.stream()\n        .filter(User::isActive)\n        .map(User::getName)\n        .collect(Collectors.toList());\n}",
        "source": "synthetic",
        "notes": "Clean — idiomatic Java Streams, method references, descriptive name — Java"
    },
    {
        "id": "UC5_088", "label": "CLEAN",
        "category": "CLEAN_Pythonic", "subcategory": "Error Handling",
        "difficulty": "medium",
        "text": "def safe_divide(a: float, b: float) -> float | None:\n    if b == 0:\n        logger.warning('Division by zero attempted: a=%s', a)\n        return None\n    return a / b",
        "source": "synthetic",
        "notes": "Clean — guards against division by zero, logs warning, typed — Python"
    },
    {
        "id": "UC5_089", "label": "CLEAN",
        "category": "CLEAN_JS", "subcategory": "Async Pattern",
        "difficulty": "medium",
        "text": "async function fetchUserData(userId) {\n    const [profile, orders] = await Promise.all([\n        fetchProfile(userId),\n        fetchOrders(userId),\n    ]);\n    return { profile, orders };\n}",
        "source": "synthetic",
        "notes": "Clean — parallel async with Promise.all, destructuring — JavaScript"
    },
    {
        "id": "UC5_090", "label": "CLEAN",
        "category": "CLEAN_Java", "subcategory": "Try With Resources",
        "difficulty": "medium",
        "text": "public List<String> readLines(Path path) throws IOException {\n    try (BufferedReader reader = Files.newBufferedReader(path)) {\n        return reader.lines().collect(Collectors.toList());\n    }\n}",
        "source": "synthetic",
        "notes": "Clean — try-with-resources, streams, proper exception declaration — Java"
    },
    {
        "id": "UC5_091", "label": "CLEAN",
        "category": "CLEAN_Pythonic", "subcategory": "Dataclass",
        "difficulty": "medium",
        "text": "@dataclass(frozen=True)\nclass Money:\n    amount: Decimal\n    currency: str = 'USD'\n\n    def __add__(self, other: 'Money') -> 'Money':\n        if self.currency != other.currency:\n            raise ValueError(f'Cannot add {self.currency} and {other.currency}')\n        return Money(self.amount + other.amount, self.currency)",
        "source": "synthetic",
        "notes": "Clean — frozen dataclass, Decimal for money, currency validation — Python"
    },
    {
        "id": "UC5_092", "label": "CLEAN",
        "category": "CLEAN_JS", "subcategory": "Middleware Pattern",
        "difficulty": "medium",
        "text": "const rateLimit = (maxRequests, windowMs) => {\n    const hits = new Map();\n    return (req, res, next) => {\n        const key = req.ip;\n        const now = Date.now();\n        const record = hits.get(key) || { count: 0, start: now };\n        if (now - record.start > windowMs) {\n            record.count = 0; record.start = now;\n        }\n        if (++record.count > maxRequests) return res.status(429).end();\n        hits.set(key, record);\n        next();\n    };\n};",
        "source": "synthetic",
        "notes": "Clean — rate limiter middleware with sliding window, parameterized — Node.js"
    },
    {
        "id": "UC5_093", "label": "CLEAN",
        "category": "CLEAN_Pythonic", "subcategory": "Generator",
        "difficulty": "medium",
        "text": "def chunked(iterable, size: int):\n    it = iter(iterable)\n    while chunk := list(islice(it, size)):\n        yield chunk",
        "source": "synthetic",
        "notes": "Clean — memory-efficient chunking with generator and walrus operator — Python"
    },
    {
        "id": "UC5_094", "label": "CLEAN",
        "category": "CLEAN_Java", "subcategory": "Builder Pattern",
        "difficulty": "medium",
        "text": "HttpRequest request = HttpRequest.newBuilder()\n    .uri(URI.create(url))\n    .header(\"Authorization\", \"Bearer \" + token)\n    .timeout(Duration.ofSeconds(10))\n    .GET()\n    .build();",
        "source": "synthetic",
        "notes": "Clean — builder pattern, timeout set, clear fluent API usage — Java"
    },
    {
        "id": "UC5_095", "label": "CLEAN",
        "category": "CLEAN_Pythonic", "subcategory": "Decorator",
        "difficulty": "hard",
        "text": "def retry(max_attempts: int = 3, delay: float = 1.0):\n    def decorator(func):\n        @functools.wraps(func)\n        def wrapper(*args, **kwargs):\n            for attempt in range(max_attempts):\n                try:\n                    return func(*args, **kwargs)\n                except Exception:\n                    if attempt == max_attempts - 1:\n                        raise\n                    time.sleep(delay * (2 ** attempt))\n        return wrapper\n    return decorator",
        "source": "synthetic",
        "notes": "Clean — retry decorator with exponential backoff, preserves metadata — Python"
    },
    {
        "id": "UC5_096", "label": "CLEAN",
        "category": "CLEAN_JS", "subcategory": "Error Boundary",
        "difficulty": "hard",
        "text": "class ErrorBoundary extends React.Component {\n    state = { error: null };\n    static getDerivedStateFromError(error) { return { error }; }\n    componentDidCatch(error, info) { logService.report(error, info); }\n    render() {\n        return this.state.error\n            ? <FallbackUI error={this.state.error} />\n            : this.props.children;\n    }\n}",
        "source": "synthetic",
        "notes": "Clean — proper React error boundary with logging and fallback UI — React"
    },
    {
        "id": "UC5_097", "label": "CLEAN",
        "category": "CLEAN_Java", "subcategory": "Concurrency",
        "difficulty": "hard",
        "text": "private final ConcurrentHashMap<String, AtomicLong> counters = new ConcurrentHashMap<>();\n\npublic long increment(String key) {\n    return counters.computeIfAbsent(key, k -> new AtomicLong(0)).incrementAndGet();\n}",
        "source": "synthetic",
        "notes": "Clean — thread-safe counter with ConcurrentHashMap and AtomicLong — Java"
    },
    {
        "id": "UC5_098", "label": "CLEAN",
        "category": "CLEAN_Pythonic", "subcategory": "Async Context Manager",
        "difficulty": "hard",
        "text": "class DBPool:\n    async def __aenter__(self):\n        self.pool = await asyncpg.create_pool(dsn=self.dsn, min_size=2, max_size=10)\n        return self.pool\n\n    async def __aexit__(self, *exc):\n        await self.pool.close()",
        "source": "synthetic",
        "notes": "Clean — async context manager for connection pool lifecycle — Python"
    },
    {
        "id": "UC5_099", "label": "CLEAN",
        "category": "CLEAN_JS", "subcategory": "Debounce",
        "difficulty": "hard",
        "text": "function debounce(fn, ms) {\n    let timer;\n    return (...args) => {\n        clearTimeout(timer);\n        timer = setTimeout(() => fn.apply(this, args), ms);\n    };\n}",
        "source": "synthetic",
        "notes": "Clean — classic debounce implementation, concise and correct — JavaScript"
    },
    {
        "id": "UC5_100", "label": "CLEAN",
        "category": "CLEAN_Java", "subcategory": "Immutable Record",
        "difficulty": "hard",
        "text": "public record PageRequest(int page, int size) {\n    public PageRequest {\n        if (page < 0) throw new IllegalArgumentException(\"page must be >= 0\");\n        if (size < 1 || size > 100) throw new IllegalArgumentException(\"size must be 1-100\");\n    }\n    public int offset() { return page * size; }\n}",
        "source": "synthetic",
        "notes": "Clean — Java record with compact constructor validation and derived method — Java"
    },
]


def build_csv():
    """Write gold set to CSV with all metadata columns."""
    filepath = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    fieldnames = [
        "id", "text", "label", "category", "subcategory",
        "difficulty", "source", "notes",
        "split"  # train or test
    ]

    # Assign 70/30 train/test split preserving category balance (stratified)
    # 20 items per label: 14 train, 6 test per label = 70 train, 30 test total
    labels = ["SECURITY", "LOGIC_ERROR", "PERFORMANCE", "BEST_PRACTICE", "CLEAN"]
    for label in labels:
        label_items = [x for x in GOLD_SET if x["label"] == label]
        for i, item in enumerate(label_items):
            item["split"] = "train" if i < 14 else "test"

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(GOLD_SET)

    return filepath


def build_metadata():
    """Write metadata JSON for paper appendix reference."""
    labels = ["SECURITY", "LOGIC_ERROR", "PERFORMANCE", "BEST_PRACTICE", "CLEAN"]

    meta = {
        "use_case": "UC5",
        "name": "Automated Code Review",
        "task": "5-way classification of code snippet primary issue type",
        "pre_registration_date": "2026-03-02",
        "version": "1.0",
        "total_items": len(GOLD_SET),
        "label_distribution": {
            label: len([x for x in GOLD_SET if x["label"] == label])
            for label in labels
        },
        "labels": [
            "SECURITY — SQL injection, XSS, command injection, hardcoded secrets, auth bypass",
            "LOGIC_ERROR — Off-by-one, null/undefined access, wrong condition, infinite loop, race condition",
            "PERFORMANCE — N+1 queries, unnecessary allocation, blocking I/O in async, quadratic complexity",
            "BEST_PRACTICE — Magic numbers, poor naming, missing error handling, tight coupling, no validation",
            "CLEAN — No issues (well-written code)",
        ],
        "languages": ["Python", "JavaScript", "Java"],
        "category_breakdown": {
            # SECURITY subcategories
            "SEC_Injection": len([x for x in GOLD_SET if x["category"] == "SEC_Injection"]),
            "SEC_Secrets": len([x for x in GOLD_SET if x["category"] == "SEC_Secrets"]),
            "SEC_XSS": len([x for x in GOLD_SET if x["category"] == "SEC_XSS"]),
            "SEC_Auth": len([x for x in GOLD_SET if x["category"] == "SEC_Auth"]),
            # LOGIC_ERROR subcategories
            "LOGIC_Boundary": len([x for x in GOLD_SET if x["category"] == "LOGIC_Boundary"]),
            "LOGIC_Null": len([x for x in GOLD_SET if x["category"] == "LOGIC_Null"]),
            "LOGIC_Condition": len([x for x in GOLD_SET if x["category"] == "LOGIC_Condition"]),
            "LOGIC_Loop": len([x for x in GOLD_SET if x["category"] == "LOGIC_Loop"]),
            "LOGIC_Race": len([x for x in GOLD_SET if x["category"] == "LOGIC_Race"]),
            # PERFORMANCE subcategories
            "PERF_Complexity": len([x for x in GOLD_SET if x["category"] == "PERF_Complexity"]),
            "PERF_Query": len([x for x in GOLD_SET if x["category"] == "PERF_Query"]),
            "PERF_Allocation": len([x for x in GOLD_SET if x["category"] == "PERF_Allocation"]),
            "PERF_IO": len([x for x in GOLD_SET if x["category"] == "PERF_IO"]),
            # BEST_PRACTICE subcategories
            "BP_Naming": len([x for x in GOLD_SET if x["category"] == "BP_Naming"]),
            "BP_Magic": len([x for x in GOLD_SET if x["category"] == "BP_Magic"]),
            "BP_ErrorHandling": len([x for x in GOLD_SET if x["category"] == "BP_ErrorHandling"]),
            "BP_Coupling": len([x for x in GOLD_SET if x["category"] == "BP_Coupling"]),
            "BP_Validation": len([x for x in GOLD_SET if x["category"] == "BP_Validation"]),
            # CLEAN subcategories
            "CLEAN_Pythonic": len([x for x in GOLD_SET if x["category"] == "CLEAN_Pythonic"]),
            "CLEAN_JS": len([x for x in GOLD_SET if x["category"] == "CLEAN_JS"]),
            "CLEAN_Java": len([x for x in GOLD_SET if x["category"] == "CLEAN_Java"]),
        },
        "difficulty_distribution": {
            "easy":   len([x for x in GOLD_SET if x["difficulty"] == "easy"]),
            "medium": len([x for x in GOLD_SET if x["difficulty"] == "medium"]),
            "hard":   len([x for x in GOLD_SET if x["difficulty"] == "hard"]),
        },
        "train_test_split": {
            "train": len([x for x in GOLD_SET if x.get("split") == "train"]),
            "test":  len([x for x in GOLD_SET if x.get("split") == "test"]),
        },
        "s3_score": {
            "value": 3.33,
            "tier": "Hybrid",
            "note": "First formula-only Hybrid case in the study (no Flag Rule triggered)",
            "dimensions": {
                "task_complexity": {"score": 4, "weight": 3, "rationale": "Multi-step code analysis"},
                "output_structure": {"score": 3, "weight": 2, "rationale": "Single classification label from closed set"},
                "stakes": {"score": 3, "weight": 4, "rationale": "Missed bugs reach production, but software can be patched"},
                "data_sensitivity": {"score": 3, "weight": 2, "rationale": "Proprietary source code"},
                "latency_requirement": {"score": 4, "weight": 3, "rationale": "Near real-time, developer waiting for PR review"},
                "volume": {"score": 2, "weight": 1, "rationale": "Hundreds per day"},
            },
            "calculation": "((4*3)+(3*2)+(3*4)+(3*2)+(4*3)+(2*1)) / (5*(3+2+4+2+3+1)) * 5 = 50/75 * 5 = 3.33",
            "flag_rule": "NO Flag Rule triggered (Stakes=3 < 4)",
        },
        "evaluation_metrics": [
            "Exact Match Rate (accuracy)",
            "Macro F1 Score (5-class)",
            "Per-Class Precision / Recall",
            "Confusion Matrix",
            "Latency P50/P95 (ms)",
            "Cost Per Successful Task (CPS)",
        ],
        "pre_registered_hypotheses": [
            "H5.1: Best SLM achieves >= 85% of LLM accuracy on code review classification",
            "H5.2: Best SLM P95 latency < 4000ms (batch processing SLA)",
            "H5.3: UC5 validates as Hybrid tier — no SLM achieves >= 95% LLM parity (confirming S3=3.33 prediction)",
            "H5.4: SECURITY class will have highest SLM-LLM gap (requires domain-specific reasoning)",
        ],
        "created_at": datetime.now().isoformat(),
    }

    meta_path = os.path.join(OUTPUT_DIR, META_FILE)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return meta_path


def print_summary():
    """Print verification summary to confirm gold set is correct."""
    labels = ["SECURITY", "LOGIC_ERROR", "PERFORMANCE", "BEST_PRACTICE", "CLEAN"]

    print()
    print("=" * 62)
    print("  UC5 GOLD SET — Build Complete")
    print("  Automated Code Review — Pre-Registration v1.0")
    print("=" * 62)
    print()
    print(f"  Total items  : {len(GOLD_SET)}")
    for label in labels:
        n = len([x for x in GOLD_SET if x["label"] == label])
        print(f"  {label:<16}: {n} items (20%)")
    print()

    print("  S3 Score     : 3.33 -> Hybrid (formula-only, no Flag Rule)")
    print()

    print("  Category breakdown:")
    label_cats = {
        "SECURITY": [
            ("SEC_Injection", "Injection (SQL, Cmd, Code, SSRF, Deser)"),
            ("SEC_Secrets",   "Hardcoded Secrets / Credentials"),
            ("SEC_XSS",       "Cross-Site Scripting (XSS)"),
            ("SEC_Auth",      "Auth Bypass / IDOR / JWT"),
        ],
        "LOGIC_ERROR": [
            ("LOGIC_Boundary",  "Boundary / Off-by-One"),
            ("LOGIC_Null",      "Null / Undefined Access"),
            ("LOGIC_Condition", "Wrong Condition / Type Coercion"),
            ("LOGIC_Loop",      "Loop / Iteration Bugs"),
            ("LOGIC_Race",      "Race Conditions / TOCTOU"),
        ],
        "PERFORMANCE": [
            ("PERF_Complexity",  "Algorithmic Complexity"),
            ("PERF_Query",       "Database Query Issues"),
            ("PERF_Allocation",  "Memory / Allocation Waste"),
            ("PERF_IO",          "Blocking / Sequential I/O"),
        ],
        "BEST_PRACTICE": [
            ("BP_Naming",        "Poor / Misleading Naming"),
            ("BP_Magic",         "Magic Numbers / Strings"),
            ("BP_ErrorHandling", "Error Handling Issues"),
            ("BP_Coupling",      "Tight Coupling / SRP"),
            ("BP_Validation",    "Missing Input Validation"),
        ],
        "CLEAN": [
            ("CLEAN_Pythonic", "Python (idiomatic)"),
            ("CLEAN_JS",       "JavaScript / Node.js"),
            ("CLEAN_Java",     "Java (idiomatic)"),
        ],
    }
    for label in labels:
        print(f"\n  {label}:")
        for cat, desc in label_cats[label]:
            n = len([x for x in GOLD_SET if x["category"] == cat])
            print(f"    {desc:<42} {n} items")

    print()
    print("  Difficulty distribution:")
    for diff in ["easy", "medium", "hard"]:
        n = len([x for x in GOLD_SET if x["difficulty"] == diff])
        bar = "█" * n
        print(f"    {diff:<8} {bar:<50} {n}")

    train_n = len([x for x in GOLD_SET if x.get("split") == "train"])
    test_n  = len([x for x in GOLD_SET if x.get("split") == "test"])
    print()
    print(f"  Train / Test split : {train_n} train / {test_n} test (70/30 stratified)")
    print()
    print("  Files saved:")
    print(f"    data/gold_sets/{OUTPUT_FILE}")
    print(f"    data/gold_sets/{META_FILE}")
    print()
    print("  ✅  Gold set locked — DO NOT MODIFY after this point")
    print("      This is your pre-registered ground truth.")
    print()
    print("  NEXT STEP:")
    print("  → python3 scripts/run_benchmark_uc5.py")
    print("  → Runs all 7 models against UC5 test set (30 items × 7 models × 3 runs)")
    print("=" * 62)
    print()


if __name__ == "__main__":
    print()
    print("Building UC5 Gold Set — Automated Code Review...")
    csv_path  = build_csv()
    meta_path = build_metadata()
    print_summary()
