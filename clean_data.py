import csv
import re
import io
import html
from datetime import datetime

def normalize_timestamp(ts):
    if not ts or ts.strip() == '':
        return ''
    ts = ts.strip()
    # Unix epoch (10 digits)
    if re.match(r'^\d{10}$', ts):
        try:
            return datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%dT%H:%M:%S')
        except:
            return ts
    # ISO 8601
    if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$', ts):
        return ts
    # DD-MM-YYYY
    m = re.match(r'^(\d{2})-(\d{2})-(\d{4})$', ts)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}T00:00:00"
    return ts

def clean_text(text):
    if not text or text.strip() == '':
        return ''
    text = html.unescape(text)
    text = re.sub(r'<div>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Ã©', '\u00e9', text)
    text = text.replace('&amp;', '&')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_likes(val):
    if not val or val.strip() == '':
        return None
    val = val.strip()
    if val.upper() == 'NULL':
        return None
    try:
        v = float(val)
        if v < 0:
            v = abs(v)
        return int(v)
    except:
        return None

def clean_int(val):
    if not val or val.strip() == '':
        return None
    val = val.strip()
    if val.upper() == 'NULL':
        return None
    try:
        return int(float(val))
    except:
        return None

def clean_posts(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    reader = csv.reader(io.StringIO(content))
    header = next(reader)
    
    rows = []
    i = 0
    all_rows = list(reader)
    
    while i < len(all_rows):
        row = all_rows[i]
        if len(row) >= len(header):
            rows.append(row[:len(header)])
            i += 1
        elif len(row) > 0 and i + 1 < len(all_rows):
            merged = row.copy()
            while len(merged) < len(header) and i + 1 < len(all_rows):
                i += 1
                next_row = all_rows[i]
                merged[-1] = merged[-1] + ' ' + next_row[0]
                merged.extend(next_row[1:])
            rows.append(merged[:len(header)])
            i += 1
        else:
            if any(cell.strip() for cell in row):
                padded = row + [''] * (len(header) - len(row))
                rows.append(padded[:len(header)])
            i += 1
    
    cleaned = []
    for row in rows:
        if len(row) < len(header):
            row = row + [''] * (len(header) - len(row))
        elif len(row) > len(header):
            row = row[:len(header)]
        
        post_id = row[0].strip() if row[0] else ''
        user_id = row[1].strip() if row[1] else ''
        platform = row[2].strip() if row[2] else ''
        text_content = row[3].strip() if row[3] else ''
        timestamp = row[4].strip() if row[4] else ''
        likes_raw = row[5].strip() if row[5] else ''
        shares = row[6].strip() if row[6] else ''
        comments = row[7].strip() if row[7] else ''
        
        if platform.upper() == 'NULL' or platform == '':
            platform = 'Unknown'
        
        text_content = clean_text(text_content)
        if not text_content or text_content.upper() == 'NULL':
            text_content = '[No text]'
        
        timestamp = normalize_timestamp(timestamp)
        
        likes_clean = clean_likes(likes_raw)
        shares_clean = clean_int(shares)
        comments_clean = clean_int(comments)
        
        cleaned.append([
            post_id, user_id, platform, text_content,
            timestamp,
            str(likes_clean) if likes_clean is not None else '',
            str(shares_clean) if shares_clean is not None else '',
            str(comments_clean) if comments_clean is not None else ''
        ])
    
    like_vals = [int(r[5]) for r in cleaned if r[5]]
    if like_vals:
        like_vals.sort()
        n = len(like_vals)
        mid = n // 2
        median_likes = like_vals[mid] if n % 2 == 1 else (like_vals[mid - 1] + like_vals[mid]) / 2
        for r in cleaned:
            if not r[5]:
                r[5] = str(int(median_likes))
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(cleaned)
    
    return len(cleaned)

def clean_users(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    reader = csv.reader(io.StringIO(content))
    header = next(reader)
    
    cleaned = []
    for row in reader:
        if len(row) < len(header):
            row = row + [''] * (len(header) - len(row))
        elif len(row) > len(header):
            row = row[:len(header)]
        
        cleaned.append([cell.strip() for cell in row])
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(cleaned)
    
    return len(cleaned)

if __name__ == '__main__':
    base = r'C:\Users\Admin\Desktop\DataVortex'
    
    posts_in = base + r'\Social_Engine_Posts_Corrupted.csv'
    posts_out = base + r'\Social_Engine_Posts_Cleaned.csv'
    users_in = base + r'\Social_Engine_Users.csv'
    users_out = base + r'\Social_Engine_Users_Cleaned.csv'
    
    print("Cleaning posts...")
    n_posts = clean_posts(posts_in, posts_out)
    print(f"  -> {n_posts} posts cleaned -> {posts_out}")
    
    print("Cleaning users...")
    n_users = clean_users(users_in, users_out)
    print(f"  -> {n_users} users cleaned -> {users_out}")
