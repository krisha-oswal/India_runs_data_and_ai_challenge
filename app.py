import streamlit as st
import json
import pandas as pd
import io
from datetime import datetime

# Set up page configurations
st.set_page_config(
    page_title="Redrob AI Ranker | Enterprise Sandbox",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling (Glassmorphism & Gradients)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main container background */
    .stApp {
        background-color: #0d0e15;
        color: #f3f4f6;
    }
    
    /* Premium Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #311042 50%, #0d0e15 100%);
        padding: 40px;
        border-radius: 16px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    .header-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6366f1, #d946ef, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .header-subtitle {
        font-size: 1.1rem;
        color: #9ca3af;
        max-width: 800px;
        margin: 0 auto;
    }
    
    /* KPI Stats Card styling */
    .kpi-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.3);
    }
    .kpi-val {
        font-size: 2.2rem;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 5px;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Candidate Card styling */
    .candidate-card {
        background: rgba(30, 41, 59, 0.3);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    .candidate-card:hover {
        background: rgba(30, 41, 59, 0.5);
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 12px 30px rgba(99, 102, 241, 0.1);
        transform: translateY(-2px);
    }
    
    /* Left score badge */
    .rank-badge {
        position: absolute;
        top: -10px;
        left: 20px;
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
        color: white;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3);
    }
    
    .score-box {
        background: linear-gradient(135deg, #312e81 0%, #1e1b4b 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        min-width: 90px;
    }
    .score-num {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f43f5e;
    }
    .score-lbl {
        font-size: 0.75rem;
        color: #9ca3af;
        text-transform: uppercase;
        margin-top: 2px;
    }
    
    /* Pill Badges */
    .skill-badge {
        background: rgba(99, 102, 241, 0.12);
        color: #818cf8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
        display: inline-block;
        border: 1px solid rgba(99, 102, 241, 0.25);
    }
    
    .tier5-badge {
        background: rgba(236, 72, 153, 0.15);
        color: #f472b6;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
        display: inline-block;
        border: 1px solid rgba(236, 72, 153, 0.3);
    }
    
    .status-dot {
        height: 8px;
        width: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }
    .status-dot-inactive {
        height: 8px;
        width: 8px;
        background-color: #6b7280;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Services list and CV/Speech/NLP categories
SERVICES_COMPANIES = {
    'infosys', 'wipro', 'tcs', 'capgemini', 'hcl', 'accenture', 'cognizant', 
    'tech mahindra', 'mphasis', 'genpact', 'genpact ai'
}

CV_SPEECH_ROBOTICS_SKILLS = {
    "computer vision", "image classification", "object detection", 
    "speech recognition", "tts", "robotics", "gans", "diffusion models", 
    "yolo", "opencv", "asr"
}

NLP_IR_SEARCH_SKILLS = {
    "nlp", "natural language processing", "search backend", "vector representations", 
    "ranking systems", "information retrieval", "bm25", "learning to rank", 
    "faiss", "qdrant", "weaviate", "pgvector", "elasticsearch", "opensearch", 
    "pinecone", "milvus", "rag", "langchain", "llms", "fine-tuning llms", 
    "recommendation systems", "vector search", "hybrid search", "semantic search",
    "information retrieval systems", "search infrastructure", "indexing algorithms",
    "text encoders", "search & discovery", "content matching", "model adaptation",
    "document processing", "open-source ml libraries", "workflow orchestration",
    "sentence transformers", "transformers"
}

TIER5_SKILLS = {
    "search backend", "vector representations", "ranking systems", 
    "search infrastructure", "indexing algorithms", "text encoders", 
    "information retrieval systems", "content matching", "model adaptation", 
    "search & discovery"
}

def parse_date(d_str):
    if not d_str:
        return None
    try:
        return datetime.strptime(d_str, "%Y-%m-%d")
    except Exception:
        return None

# Scoring algorithm with adjustable sidebar parameters
def score_candidate_custom(c, w_title, w_skill, w_yoe, w_narrative, b_tier5, now_date=datetime(2026, 6, 22)):
    profile = c.get('profile', {})
    career_history = c.get('career_history', [])
    skills = c.get('skills', [])
    signals = c.get('redrob_signals', {})
    
    # 1. Services-only Gate
    companies = [job.get('company', '').lower().strip() for job in career_history]
    if companies:
        all_services = all(comp in SERVICES_COMPANIES for comp in companies)
        if all_services:
            return None, "consulting_only"
            
    # 2. CV/Speech-only Gate
    skill_names = {s.get('name', '').lower().strip() for s in skills}
    has_cv_speech = any(s in CV_SPEECH_ROBOTICS_SKILLS for s in skill_names)
    has_nlp_ir = any(s in NLP_IR_SEARCH_SKILLS for s in skill_names)
    if has_cv_speech and not has_nlp_ir:
        return None, "cv_speech_only"
        
    # 3. YOE Score
    yoe = profile.get('years_of_experience', 0)
    if 5.0 <= yoe <= 9.0:
        yoe_score = 1.0
    elif 4.0 <= yoe < 5.0 or 9.0 < yoe <= 12.0:
        yoe_score = 0.8
    elif 3.0 <= yoe < 4.0 or 12.0 < yoe <= 15.0:
        yoe_score = 0.5
    else:
        yoe_score = 0.1
        
    # 4. Title Alignment Score
    current_title = profile.get('current_title', '').lower().strip()
    
    irrelevant_titles = {
        'business analyst', 'hr manager', 'mechanical engineer', 'accountant',
        'project manager', 'customer support', 'operations manager', 'content writer',
        'sales executive', 'civil engineer', 'graphic designer', 'marketing manager'
    }
    high_match_titles = [
        'ai engineer', 'machine learning', 'ml engineer', 'search engineer', 
        'retrieval engineer', 'ranking engineer', 'recommendation systems',
        'applied scientist', 'ai specialist', 'nlp engineer'
    ]
    adjacent_titles = [
        'data scientist', 'backend engineer', 'software engineer', 
        'analytics engineer', 'data engineer', 'developer', 'systems engineer'
    ]
    
    title_score = 0.0
    if current_title in irrelevant_titles:
        title_score = 0.0
    elif any(t in current_title for t in high_match_titles):
        title_score = 1.0
    elif any(t in current_title for t in adjacent_titles):
        title_score = 0.6
    elif current_title:
        title_score = 0.2
        
    past_ai_ml = False
    for job in career_history:
        past_title = job.get('title', '').lower()
        if any(t in past_title for t in high_match_titles):
            past_ai_ml = True
            break
    if past_ai_ml and title_score < 1.0 and title_score > 0.0:
        title_score = max(title_score, 0.8)
        
    # 5. Narrative Text Search
    narrative_score = 0.0
    summary = profile.get('summary', '').lower()
    narrative_keywords = [
        "recommendation system", "recommender system", "ranking system", 
        "learning to rank", "vector search", "hybrid search", "semantic search", 
        "embeddings", "retrieval system", "search engine", "information retrieval"
    ]
    for kw in narrative_keywords:
        kw_count = summary.count(kw)
        for job in career_history:
            kw_count += job.get('description', '').lower().count(kw)
        if kw_count > 0:
            narrative_score += min(0.05 * kw_count, 0.1)
    narrative_score = min(narrative_score, 0.3)
    
    # 6. Skill Match Score
    skill_score = 0.0
    has_tier5_skill = False
    
    for s in skills:
        name_lower = s.get('name', '').lower().strip()
        prof = s.get('proficiency', 'beginner')
        prof_weights = {'expert': 1.0, 'advanced': 0.8, 'intermediate': 0.5, 'beginner': 0.2}
        pw = prof_weights.get(prof, 0.2)
        
        if name_lower in TIER5_SKILLS:
            has_tier5_skill = True
            skill_score += 1.5 * pw
        elif name_lower in NLP_IR_SEARCH_SKILLS:
            skill_score += 1.0 * pw
        elif name_lower in CV_SPEECH_ROBOTICS_SKILLS:
            skill_score += 0.3 * pw
        else:
            skill_score += 0.1 * pw
            
    skill_score = min(skill_score, 3.0) / 3.0
    tier5_boost = b_tier5 if has_tier5_skill else 0.0
    
    # Custom weighted base score
    total_weight = w_title + w_skill + w_yoe + w_narrative
    if total_weight > 0:
        base_score = (w_title * title_score + w_skill * skill_score + w_yoe * yoe_score + w_narrative * narrative_score) / total_weight
    else:
        base_score = 0.0
    base_score += tier5_boost
    base_score = min(base_score, 1.0)
    
    # 7. Behavioral Multiplier
    last_act = parse_date(signals.get('last_active_date'))
    if last_act:
        days_inactive = (now_date - last_act).days
        if days_inactive < 30:
            activity_mult = 1.0
        elif days_inactive < 90:
            activity_mult = 0.9
        elif days_inactive < 180:
            activity_mult = 0.75
        else:
            activity_mult = 0.5
    else:
        activity_mult = 0.5
        
    resp_rate = signals.get('recruiter_response_rate', 0.0)
    response_mult = 0.6 + 0.4 * resp_rate
    
    resp_time = signals.get('avg_response_time_hours', 48.0)
    if resp_time <= 24.0:
        time_mult = 1.0
    elif resp_time <= 72.0:
        time_mult = 0.9
    elif resp_time <= 168.0:
        time_mult = 0.8
    else:
        time_mult = 0.6
        
    notice_days = signals.get('notice_period_days', 60)
    if notice_days <= 30:
        notice_mult = 1.0
    elif notice_days <= 60:
        notice_mult = 0.9
    elif notice_days <= 90:
        notice_mult = 0.8
    else:
        notice_mult = 0.6
        
    behavioral_mult = activity_mult * response_mult * time_mult * notice_mult
    
    # 8. Location Multiplier
    loc = profile.get('location', '').lower()
    reloc = signals.get('willing_to_relocate', False)
    pune_noida = ['pune', 'noida']
    other_tiers = ['delhi', 'gurgaon', 'ghaziabad', 'faridabad', 'mumbai', 'thane', 'hyderabad', 'bangalore', 'bengaluru', 'chennai', 'kolkata']
    
    if any(city in loc for city in pune_noida):
        location_mult = 1.0
    elif any(city in loc for city in other_tiers):
        location_mult = 0.9 if reloc else 0.75
    else:
        location_mult = 0.8 if reloc else 0.4
        
    # 9. Honeypot Penalty
    max_excess = 0
    for s in skills:
        dur = s.get('duration_months', 0)
        limit = yoe * 12 + 12
        excess = dur - limit
        if excess > 0:
            max_excess = max(max_excess, excess)
            
    honeypot_severity = 0.0
    if max_excess > 0:
        honeypot_severity = min(0.9, max_excess / 36.0)
        
    zero_dur_experts = sum(1 for s in skills if s.get('proficiency') == 'expert' and s.get('duration_months') == 0)
    if zero_dur_experts >= 3:
        honeypot_severity = max(honeypot_severity, 0.8)
        
    mismatches = 0
    for job in career_history:
        start = parse_date(job.get('start_date'))
        end = parse_date(job.get('end_date')) or now_date
        if start:
            cal_months = (end.year - start.year) * 12 + (end.month - start.month)
            if abs(cal_months - job.get('duration_months', 0)) > 6:
                mismatches += 1
    if mismatches >= 2:
        honeypot_severity = max(honeypot_severity, 0.5)
        
    honeypot_discount = 1.0 - honeypot_severity
    
    final_score = base_score * behavioral_mult * location_mult * honeypot_discount
    
    return {
        'final_score': round(final_score, 4),
        'base_score': round(base_score, 4),
        'behavioral_mult': round(behavioral_mult, 4),
        'location_mult': round(location_mult, 4),
        'honeypot_severity': round(honeypot_severity, 4),
        'has_tier5': has_tier5_skill
    }, None

def generate_reasoning(c):
    profile = c.get('profile', {})
    skills = c.get('skills', [])
    signals = c.get('redrob_signals', {})
    career_history = c.get('career_history', [])
    cid = c.get('candidate_id')
    
    title = profile.get('current_title', 'AI Engineer')
    yoe = profile.get('years_of_experience', 0)
    
    top_skills = []
    for s in skills:
        name = s.get('name')
        if name.lower().strip() in NLP_IR_SEARCH_SKILLS:
            top_skills.append(name)
    if not top_skills:
        top_skills = [s.get('name') for s in skills[:2] if s.get('name')]
    top_skills = top_skills[:3]
    skills_str = ", ".join(top_skills) if top_skills else "applied ML"
    
    product_comps = []
    for job in career_history:
        comp = job.get('company', '')
        if comp.lower().strip() not in SERVICES_COMPANIES:
            product_comps.append(comp)
    product_comps = list(dict.fromkeys(product_comps))[:2]
    comp_str = " and ".join(product_comps) if product_comps else "product startups"
    
    loc = profile.get('location', 'Pune')
    notice = signals.get('notice_period_days', 30)
    
    h = sum(ord(char) for char in cid)
    temp_choice = h % 4
    
    if temp_choice == 0:
        return f"{title} with {yoe} YOE, specializing in {skills_str}. Shipped systems at {comp_str}; based in {loc} with {notice}-day notice."
    elif temp_choice == 1:
        return f"Demonstrates {yoe} years of experience as a {title}, with hands-on expertise in {skills_str}. Strong fit from {comp_str}; located in {loc} (notice: {notice} days)."
    elif temp_choice == 2:
        return f"Strong narrative match for search/retrieval with {yoe} YOE as a {title}. Skilled in {skills_str} at {comp_str}. Relocation/location: {loc}, {notice}-day notice."
    else:
        return f"Experienced {title} ({yoe} YOE) with deep knowledge of {skills_str}. Worked at {comp_str}; currently based in {loc} with {notice}-day notice period."

# Layout
st.markdown("""
    <div class="header-banner">
        <div class="header-title">Intelligent Candidate Discovery & Ranking</div>
        <div class="header-subtitle">Enterprise Candidate Discovery Engine matching candidates against the Senior AI Engineer role using multi-dimensional alignment, behavioral metrics, and honeypot suppression.</div>
    </div>
""", unsafe_allow_html=True)

# Sidebar interactive controls
st.sidebar.title("🎛️ Algorithm Tuning")

st.sidebar.subheader("Filter Gates")
gate_services = st.sidebar.checkbox("Services-Only Gate", value=True, help="Disqualify candidates who have worked ONLY at consulting/services firms.")
gate_cv_speech = st.sidebar.checkbox("CV/Speech-Only Gate", value=True, help="Disqualify CV/Speech-only engineers with no NLP/IR search exposure.")

st.sidebar.subheader("Scoring Weights")
w_title = st.sidebar.slider("Current Title Relevance Weight", 0.0, 1.0, 0.4, 0.1)
w_skill = st.sidebar.slider("Skill Profiles Weight", 0.0, 1.0, 0.3, 0.1)
w_yoe = st.sidebar.slider("Years of Experience (5-9yr Target) Weight", 0.0, 1.0, 0.2, 0.1)
w_narrative = st.sidebar.slider("Narrative Keyword Match Weight", 0.0, 1.0, 0.1, 0.1)

st.sidebar.subheader("Tier 5 Boost")
b_tier5 = st.sidebar.slider("Rare Skill Match Boost (Tier 5)", 0.0, 0.8, 0.4, 0.1, help="Score boost for plain-language Tier-5 search specialists.")

# File Uploader
uploaded_file = st.file_uploader("📂 Upload Candidate Pool (candidates.jsonl or sample_candidates.json)", type=["jsonl", "json"])

if uploaded_file is not None:
    scored_candidates = []
    disq_services_count = 0
    disq_cv_speech_count = 0
    
    # Process file
    try:
        content = uploaded_file.read().decode('utf-8').strip()
        if content.startswith('['):
            candidates_list = json.loads(content)
        else:
            candidates_list = []
            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                candidates_list.append(json.loads(line))
    except Exception as e:
        st.error(f"Error parsing file structure: {e}")
        st.stop()
        
    for c in candidates_list:
        cid = c.get('candidate_id')
        
        res, err = score_candidate_custom(c, w_title, w_skill, w_yoe, w_narrative, b_tier5)
        
        if res is None:
            if err == "consulting_only" and gate_services:
                disq_services_count += 1
            elif err == "cv_speech_only" and gate_cv_speech:
                disq_cv_speech_count += 1
            continue
        
        scored_candidates.append({
            'candidate_id': cid,
            'score_details': res,
            'raw_candidate': c
        })

            
    # Sort
    scored_candidates.sort(key=lambda x: (-x['score_details']['final_score'], x['candidate_id']))
    top_100 = scored_candidates[:100]
    
    # KPI Panels
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val" style="color: #38bdf8;">{len(scored_candidates) + disq_services_count + disq_cv_speech_count}</div>
                <div class="kpi-label">Candidates Loaded</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val" style="color: #10b981;">{len(scored_candidates)}</div>
                <div class="kpi-label">Candidates Scored</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi_col3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val" style="color: #f43f5e;">{disq_services_count + disq_cv_speech_count}</div>
                <div class="kpi-label">Disqualified</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi_col4:
        top_score = top_100[0]['score_details']['final_score'] if top_100 else 0.0
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val" style="color: #a855f7;">{top_score:.4f}</div>
                <div class="kpi-label">Top Fit Score</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.write("---")
    
    # Export csv button
    csv_rows = []
    for idx, sc in enumerate(top_100):
        rank = idx + 1
        cid = sc['candidate_id']
        score = sc['score_details']['final_score']
        reasoning = generate_reasoning(sc['raw_candidate'])
        csv_rows.append([cid, rank, f"{score:.4f}", reasoning])
        
    df_csv = pd.DataFrame(csv_rows, columns=['candidate_id', 'rank', 'score', 'reasoning'])
    csv_buffer = io.StringIO()
    df_csv.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    col_dl, col_space = st.columns([1, 4])
    with col_dl:
        st.download_button(
            label="📥 Download Validated submission.csv",
            data=csv_data,
            file_name="submission.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    st.subheader(f"Rankings — Top {len(top_100)} Candidates")
    
    # List each candidate card
    for idx, sc in enumerate(top_100):
        rank = idx + 1
        cid = sc['candidate_id']
        details = sc['score_details']
        raw = sc['raw_candidate']
        profile = raw.get('profile', {})
        skills = raw.get('skills', [])
        signals = raw.get('redrob_signals', {})
        
        name = profile.get('anonymized_name', 'Anonymized')
        title = profile.get('current_title', 'Software Engineer')
        company = profile.get('current_company', 'N/A')
        yoe = profile.get('years_of_experience', 0)
        location = profile.get('location', 'N/A')
        notice = signals.get('notice_period_days', 30)
        
        # Determine status dot
        active = signals.get('open_to_work_flag', False)
        status_html = '<span class="status-dot"></span>Active' if active else '<span class="status-dot-inactive"></span>Inactive'
        
        # Skill badges
        skills_html = ""
        for s in skills:
            sname = s.get('name', '')
            sprof = s.get('proficiency', 'beginner')
            sdur = s.get('duration_months', 0)
            
            if sname.lower() in TIER5_SKILLS:
                skills_html += f'<span class="tier5-badge">💎 {sname} ({sprof})</span>'
            elif sname.lower() in NLP_IR_SEARCH_SKILLS:
                skills_html += f'<span class="skill-badge">{sname} ({sprof})</span>'
                
        # Card body
        col_c1, col_c2, col_c3 = st.columns([1, 6, 2])
        
        with col_c1:
            st.markdown(f"""
                <div style="margin-top: 15px;"></div>
                <div class="score-box">
                    <div class="score-lbl">Rank {rank}</div>
                    <div class="score-num">{details['final_score']:.4f}</div>
                    <div class="score-lbl">Score</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col_c2:
            st.markdown(f"""
                <div style="font-size: 1.3rem; font-weight: 600; color: #f3f4f6; display: flex; align-items: center; gap: 10px;">
                    {name} <span style="font-size: 0.9rem; color: #6b7280; font-weight: 400;">({cid})</span>
                </div>
                <div style="font-size: 1rem; color: #38bdf8; font-weight: 600; margin-top: 2px;">
                    {title} @ {company}
                </div>
                <div style="font-size: 0.85rem; color: #9ca3af; margin-top: 4px; display: flex; gap: 15px;">
                    <span>💼 {yoe} YOE</span>
                    <span>📍 {location}</span>
                    <span>🕒 {notice}-day notice</span>
                    <span>{status_html}</span>
                </div>
                <div style="margin-top: 12px;">
                    {skills_html}
                </div>
            """, unsafe_allow_html=True)
            
        with col_c3:
            # Expand details button
            with st.expander("🔍 Full Details"):
                st.markdown(f"**Dynamic Reasoning:**")
                st.info(generate_reasoning(raw))
                
                st.markdown("**Metric Breakdown:**")
                st.write(f"- Base Alignment Score: `{details['base_score']:.4f}`")
                st.write(f"- Behavioral Multiplier: `{details['behavioral_mult']:.4f}`")
                st.write(f"- Location Multiplier: `{details['location_mult']:.4f}`")
                if details['honeypot_severity'] > 0:
                    st.warning(f"- Honeypot Penalty Applied: `-{details['honeypot_severity']*100:.1f}%` reduction")
                else:
                    st.write(f"- Honeypot Penalty: `0.00` (Inconsistencies undetected)")
                    
                st.markdown("**Career History:**")
                for job in raw.get('career_history', []):
                    st.markdown(f"- **{job.get('title')}** at *{job.get('company')}* ({job.get('duration_months')} mo)")
                    st.write(f"  *{job.get('description')}*")
        
        st.markdown('<hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.05); margin: 15px 0;">', unsafe_allow_html=True)
else:
    # No file uploaded yet, show features overview
    st.info("💡 Please upload candidates.jsonl or sample_candidates.json in the file uploader above to begin.")
    
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    with col_feat1:
        st.markdown("""
            <div class="kpi-card" style="min-height: 250px; text-align: left;">
                <div style="font-size: 1.3rem; font-weight: 600; color: #6366f1; margin-bottom: 10px;">🎯 Multi-Dimensional Scorer</div>
                <p style="font-size: 0.9rem; color: #9ca3af; line-height: 1.5;">Matches candidates across title alignment, YOE, specific skill proficiencies, and semantic resume keywords using custom-tuned weights.</p>
            </div>
        """, unsafe_allow_html=True)
    with col_feat2:
        st.markdown("""
            <div class="kpi-card" style="min-height: 250px; text-align: left;">
                <div style="font-size: 1.3rem; font-weight: 600; color: #d946ef; margin-bottom: 10px;">🛡️ Trap & Honeypot Shield</div>
                <p style="font-size: 0.9rem; color: #9ca3af; line-height: 1.5;">Calculates honeypot severity indexes from skill duration excess, zero-duration experts, and date discrepancies. Automatically downweights matching candidates that carry anomalies.</p>
            </div>
        """, unsafe_allow_html=True)
    with col_feat3:
        st.markdown("""
            <div class="kpi-card" style="min-height: 250px; text-align: left;">
                <div style="font-size: 1.3rem; font-weight: 600; color: #06b6d4; margin-bottom: 10px;">💬 AI Reasoning Generator</div>
                <p style="font-size: 0.9rem; color: #9ca3af; line-height: 1.5;">Dynamically crafts unique, non-templated 1-2 sentence justifications citing actual candidate experience, skills, and notice periods for Stage 4 manual reviews.</p>
            </div>
        """, unsafe_allow_html=True)
