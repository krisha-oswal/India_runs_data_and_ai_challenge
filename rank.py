#!/usr/bin/env python3
import json
import csv
import argparse
from datetime import datetime

# Services/consulting list
SERVICES_COMPANIES = {
    'infosys', 'wipro', 'tcs', 'capgemini', 'hcl', 'accenture', 'cognizant', 
    'tech mahindra', 'mphasis', 'genpact', 'genpact ai'
}

# CV/Speech/Robotics skills
CV_SPEECH_ROBOTICS_SKILLS = {
    "computer vision", "image classification", "object detection", 
    "speech recognition", "tts", "robotics", "gans", "diffusion models", 
    "yolo", "opencv", "asr"
}

# NLP/IR/Search core skills
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

# Rare/paraphrased Tier 5 skills
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

def score_candidate(c, now_date=datetime(2026, 6, 22)):
    profile = c.get('profile', {})
    career_history = c.get('career_history', [])
    skills = c.get('skills', [])
    signals = c.get('redrob_signals', {})
    
    # 1. Services-only Gate
    companies = [job.get('company', '').lower().strip() for job in career_history]
    if companies:
        all_services = all(comp in SERVICES_COMPANIES for comp in companies)
        if all_services:
            return None # disqualified
            
    # 2. CV/Speech-only Gate
    skill_names = {s.get('name', '').lower().strip() for s in skills}
    has_cv_speech = any(s in CV_SPEECH_ROBOTICS_SKILLS for s in skill_names)
    has_nlp_ir = any(s in NLP_IR_SEARCH_SKILLS for s in skill_names)
    if has_cv_speech and not has_nlp_ir:
        return None # disqualified
        
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
        
    # Check past titles for any AI/ML roles
    past_ai_ml = False
    for job in career_history:
        past_title = job.get('title', '').lower()
        if any(t in past_title for t in high_match_titles):
            past_ai_ml = True
            break
    if past_ai_ml and title_score < 1.0 and title_score > 0.0:
        title_score = max(title_score, 0.8) # boost if they were ML in the past
        
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
            narrative_score += min(0.05 * kw_count, 0.1) # cap weight per keyword
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
            
    # Cap skill score at 3.0
    skill_score = min(skill_score, 3.0) / 3.0
    
    # Rare plain-language Tier 5 candidate boost
    tier5_boost = 0.0
    if has_tier5_skill:
        tier5_boost = 0.4
        
    # Base score
    base_score = 0.4 * title_score + 0.3 * skill_score + 0.2 * yoe_score + 0.1 * narrative_score + tier5_boost
    base_score = min(base_score, 1.0)
    
    # 7. Behavioral Multiplier
    # Recency of activity
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
        
    # Recruiter response rate
    resp_rate = signals.get('recruiter_response_rate', 0.0)
    response_mult = 0.6 + 0.4 * resp_rate
    
    # Avg response time
    resp_time = signals.get('avg_response_time_hours', 48.0)
    if resp_time <= 24.0:
        time_mult = 1.0
    elif resp_time <= 72.0:
        time_mult = 0.9
    elif resp_time <= 168.0:
        time_mult = 0.8
    else:
        time_mult = 0.6
        
    # Notice period
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
        
    # Zero-duration expert skills
    zero_dur_experts = sum(1 for s in skills if s.get('proficiency') == 'expert' and s.get('duration_months') == 0)
    if zero_dur_experts >= 3:
        honeypot_severity = max(honeypot_severity, 0.8)
        
    # Date mismatches in career history
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
    
    # We round to 4 decimal places per file format and tiebreaker constraint
    return round(final_score, 4)

def generate_reasoning(c):
    profile = c.get('profile', {})
    skills = c.get('skills', [])
    signals = c.get('redrob_signals', {})
    career_history = c.get('career_history', [])
    cid = c.get('candidate_id')
    
    title = profile.get('current_title', 'AI Engineer')
    yoe = profile.get('years_of_experience', 0)
    
    # Get top matching skills
    top_skills = []
    for s in skills:
        name = s.get('name')
        if name.lower().strip() in NLP_IR_SEARCH_SKILLS:
            top_skills.append(name)
    if not top_skills:
        top_skills = [s.get('name') for s in skills[:2] if s.get('name')]
    top_skills = top_skills[:3]
    skills_str = ", ".join(top_skills) if top_skills else "applied ML"
    
    # Get product companies
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

def main():
    parser = argparse.ArgumentParser(description='Rank candidates for the AI Engineer role.')
    parser.add_argument('--candidates', type=str, required=True, help='Path to candidates.jsonl')
    parser.add_argument('--out', type=str, required=True, help='Output path for submission CSV')
    args = parser.parse_args()
    
    print(f"Reading candidates from {args.candidates}...")
    
    scored_candidates = []
    
    with open(args.candidates, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            c = json.loads(line)
            cid = c.get('candidate_id')
            
            score = score_candidate(c)
            if score is not None:
                # We save only essential fields to minimize memory usage
                scored_candidates.append({
                    'candidate_id': cid,
                    'score': score,
                    # We store candidate object or subset to generate reasoning later only for the top 100
                    'raw_candidate': c
                })
                
    print(f"Scored {len(scored_candidates)} candidates total.")
    
    # Sort by score descending, then candidate_id ascending (deterministic tiebreaker)
    scored_candidates.sort(key=lambda x: (-x['score'], x['candidate_id']))
    
    # Select top 100
    top_100 = scored_candidates[:100]
    
    print(f"Top candidate score: {top_100[0]['score']}")
    print(f"100th candidate score: {top_100[-1]['score']}")
    
    # Generate CSV rows
    rows = []
    for idx, sc in enumerate(top_100):
        rank = idx + 1
        cid = sc['candidate_id']
        score = sc['score']
        reasoning = generate_reasoning(sc['raw_candidate'])
        rows.append([cid, rank, f"{score:.4f}", reasoning])
        
    print(f"Writing ranked results to {args.out}...")
    with open(args.out, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['candidate_id', 'rank', 'score', 'reasoning'])
        writer.writerows(rows)
        
    print("Ranking pipeline complete!")

if __name__ == '__main__':
    main()
