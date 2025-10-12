import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import os

# Configuration - Use environment variable or default to localhost
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

st.set_page_config(
    page_title="TikTok Scraper Admin",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF0050;
        margin-bottom: 1rem;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-text {
        color: #28a745;
        font-weight: bold;
    }
    .error-text {
        color: #dc3545;
        font-weight: bold;
    }
    .warning-text {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def get_stats():
    """Get system statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching stats: {str(e)}")
        return None


def get_jobs(status=None, limit=50):
    """Get jobs list"""
    try:
        params = {"limit": limit}
        if status:
            params["status"] = status
        
        response = requests.get(f"{API_BASE_URL}/jobs", params=params)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching jobs: {str(e)}")
        return []


def create_job(mode, value, limit, no_watermark, drive_folder_id=None, generate_subtitles=False):
    """Create a new job"""
    try:
        payload = {
            "mode": mode,
            "value": value,
            "limit": limit,
            "no_watermark": no_watermark,
            "generate_subtitles": generate_subtitles
        }
        
        if drive_folder_id:
            payload["drive_folder_id"] = drive_folder_id
        
        response = requests.post(f"{API_BASE_URL}/jobs", json=payload)
        
        if response.status_code == 201:
            return response.json()
        else:
            st.error(f"Error creating job: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error creating job: {str(e)}")
        return None


def get_job_details(job_id):
    """Get detailed job information"""
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/{job_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching job details: {str(e)}")
        return None


def get_videos(mode=None, value=None, limit=50):
    """Get videos list"""
    try:
        params = {"limit": limit}
        if mode:
            params["mode"] = mode
        if value:
            params["value"] = value
        
        response = requests.get(f"{API_BASE_URL}/videos", params=params)
        if response.status_code == 200:
            return response.json()
        return {"total": 0, "videos": []}
    except Exception as e:
        st.error(f"Error fetching videos: {str(e)}")
        return {"total": 0, "videos": []}


def get_scheduled_jobs():
    """Get scheduled jobs"""
    try:
        response = requests.get(f"{API_BASE_URL}/scheduled-jobs")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching scheduled jobs: {str(e)}")
        return []


def create_scheduled_job(name, mode, value, limit, interval_minutes, no_watermark):
    """Create a scheduled job"""
    try:
        payload = {
            "name": name,
            "mode": mode,
            "value": value,
            "limit": limit,
            "interval_minutes": interval_minutes,
            "no_watermark": no_watermark,
            "enabled": True
        }
        
        response = requests.post(f"{API_BASE_URL}/scheduled-jobs", json=payload)
        
        if response.status_code == 201:
            return response.json()
        else:
            st.error(f"Error creating scheduled job: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error creating scheduled job: {str(e)}")
        return None


def get_monitored_accounts():
    """Get monitored accounts"""
    try:
        response = requests.get(f"{API_BASE_URL}/monitoring/accounts")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching monitored accounts: {str(e)}")
        return []


def add_monitored_account(username):
    """Add account to monitoring"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/monitoring/accounts",
            json={"username": username}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error adding account: {str(e)}")
        return None


def remove_monitored_account(username):
    """Remove account from monitoring"""
    try:
        response = requests.delete(f"{API_BASE_URL}/monitoring/accounts/{username}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error removing account: {str(e)}")
        return None


def get_monitoring_status():
    """Get monitoring system status"""
    try:
        response = requests.get(f"{API_BASE_URL}/monitoring/status")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching status: {str(e)}")
        return None


def trigger_check_now():
    """Manually trigger a check cycle"""
    try:
        response = requests.post(f"{API_BASE_URL}/monitoring/check-now")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error triggering check: {str(e)}")
        return None


# Sidebar navigation
st.sidebar.markdown("# 🎵 TikTok Scraper")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "➕ Create Job", "📋 Jobs", "🎬 Videos", "🤖 Auto Monitoring", "⏰ Scheduled Jobs", "⚙️ Settings"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")

stats = get_stats()
if stats:
    st.sidebar.metric("Total Jobs", stats["total_jobs"])
    st.sidebar.metric("Total Videos", stats["total_videos"])
    st.sidebar.metric("Storage", f"{stats['total_storage_bytes'] / (1024**3):.2f} GB")


# Main content
if page == "📊 Dashboard":
    st.markdown('<div class="main-header">📊 Dashboard</div>', unsafe_allow_html=True)
    
    if stats:
        # Job statistics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Jobs", stats["total_jobs"])
        with col2:
            st.metric("Pending", stats["pending_jobs"], delta=None)
        with col3:
            st.metric("Running", stats["running_jobs"], delta=None)
        with col4:
            st.metric("Completed", stats["completed_jobs"], delta=None)
        with col5:
            st.metric("Failed", stats["failed_jobs"], delta=None)
        
        st.markdown("---")
        
        # Video statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Videos", stats["total_videos"])
        with col2:
            st.metric("Downloaded", stats["downloaded_videos"])
        with col3:
            st.metric("Uploaded", stats["uploaded_videos"])
        with col4:
            st.metric("Failed", stats["failed_videos"])
        
        st.markdown("---")
        
        # Storage and scheduled jobs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            storage_gb = stats["total_storage_bytes"] / (1024**3)
            st.metric("Total Storage", f"{storage_gb:.2f} GB")
        with col2:
            st.metric("Scheduled Jobs", stats["scheduled_jobs_count"])
        with col3:
            st.metric("Active Schedules", stats["active_scheduled_jobs"])
    
    st.markdown("---")
    
    # Monitoring section
    st.subheader("🤖 Auto Monitoring Status")
    
    try:
        import sys
        sys.path.append('.')
        from sqlalchemy import select
        from app.models.database import get_db
        from app.models.models import MonitoredAccount
        import asyncio
        
        async def get_monitoring_stats():
            try:
                async for db in get_db():
                    result = await db.execute(
                        select(MonitoredAccount).where(MonitoredAccount.enabled == True)
                    )
                    accounts = result.scalars().all()
                    
                    total_accounts = len(accounts)
                    total_checks = sum(acc.total_checks for acc in accounts)
                    total_new_videos = sum(acc.total_new_videos for acc in accounts)
                    
                    return {
                        'total_accounts': total_accounts,
                        'total_checks': total_checks,
                        'total_new_videos': total_new_videos,
                        'accounts': accounts
                    }
            except Exception as e:
                # Table doesn't exist yet
                return None
        
        monitoring_stats = asyncio.run(get_monitoring_stats())
        
        if monitoring_stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Monitored Accounts", monitoring_stats['total_accounts'])
            with col2:
                st.metric("Total Checks", monitoring_stats['total_checks'])
            with col3:
                st.metric("New Videos Found", monitoring_stats['total_new_videos'])
            with col4:
                if monitoring_stats['total_checks'] > 0:
                    success_rate = (monitoring_stats['total_new_videos'] / monitoring_stats['total_checks']) * 100
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                else:
                    st.metric("Success Rate", "N/A")
            
            # Show recent monitored accounts
            if monitoring_stats['accounts']:
                st.write("**Recent Activity:**")
                for acc in monitoring_stats['accounts'][:5]:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"@{acc.username}")
                    with col2:
                        st.write(f"✅ {acc.total_new_videos} videos")
                    with col3:
                        st.write(f"🔍 {acc.total_checks} checks")
        else:
            st.warning("⚠️ Auto Monitoring table not initialized. Please run database init from API.")
            st.info("Go to: `/api/v1/database/init` to create missing tables")
    
    except Exception as e:
        st.warning("⚠️ Auto Monitoring: Database not initialized")
    
    st.markdown("---")
    
    # Recent jobs
    st.subheader("Recent Jobs")
    jobs = get_jobs(limit=10)
    
    if jobs:
        jobs_data = []
        for job in jobs:
            status_emoji = {
                "pending": "⏳",
                "running": "▶️",
                "completed": "✅",
                "failed": "❌",
                "cancelled": "🚫"
            }.get(job["status"], "❓")
            
            jobs_data.append({
                "Status": f"{status_emoji} {job['status'].upper()}",
                "Mode": job["mode"],
                "Value": job["value"],
                "Progress": f"{job['progress']}%",
                "Videos": f"{job['successful_downloads']}/{job['total_videos']}",
                "Created": job["created_at"][:19]
            })
        
        df = pd.DataFrame(jobs_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No jobs found")


elif page == "➕ Create Job":
    st.markdown('<div class="main-header">➕ Create New Job</div>', unsafe_allow_html=True)
    
    with st.form("create_job_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            mode = st.selectbox("Mode", ["profile", "hashtag"])
            value = st.text_input(
                "Username / Hashtag",
                placeholder="khaby.lame or coldplay",
                help="Enter username (without @) or hashtag (without #)"
            )
        
        with col2:
            limit = st.number_input("Number of Videos", min_value=1, max_value=200, value=50)
            no_watermark = st.checkbox("Download without watermark", value=True)
            generate_subtitles = st.checkbox("Generate Arabic Subtitles", value=False, help="Generate and embed Arabic subtitles in videos")
        
        drive_folder_id = st.text_input(
            "Google Drive Folder ID (Optional)",
            placeholder="Leave empty to use default",
            help="Specify a custom Google Drive folder ID"
        )
        
        submitted = st.form_submit_button("Create Job", type="primary")
        
        if submitted:
            if not value:
                st.error("Please enter a username or hashtag")
            else:
                with st.spinner("Creating job..."):
                    job = create_job(mode, value, limit, no_watermark, drive_folder_id or None, generate_subtitles)
                    
                    if job:
                        st.success(f"✅ Job created successfully! Job ID: {job['id']}")
                        st.json(job)


elif page == "📋 Jobs":
    st.markdown('<div class="main-header">📋 Jobs</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "pending", "running", "completed", "failed", "cancelled"]
        )
    
    with col2:
        limit = st.number_input("Number of Jobs", min_value=10, max_value=200, value=50)
    
    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Get jobs
    jobs = get_jobs(
        status=None if status_filter == "All" else status_filter,
        limit=limit
    )
    
    if jobs:
        for job in jobs:
            with st.expander(
                f"{job['mode'].upper()}: {job['value']} - {job['status'].upper()} ({job['progress']}%)"
            ):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Job ID:** {job['id']}")
                    st.write(f"**Mode:** {job['mode']}")
                    st.write(f"**Value:** {job['value']}")
                    st.write(f"**Status:** {job['status']}")
                
                with col2:
                    st.write(f"**Limit:** {job['limit']}")
                    st.write(f"**No Watermark:** {'Yes' if job['no_watermark'] else 'No'}")
                    st.write(f"**Progress:** {job['progress']}%")
                    st.write(f"**Total Videos:** {job['total_videos']}")
                
                with col3:
                    st.write(f"**Successful:** {job['successful_downloads']}")
                    st.write(f"**Failed:** {job['failed_downloads']}")
                    st.write(f"**Created:** {job['created_at'][:19]}")
                    if job['completed_at']:
                        st.write(f"**Completed:** {job['completed_at'][:19]}")
                
                if job['error_message']:
                    st.error(f"Error: {job['error_message']}")
                
                if st.button(f"View Details", key=f"details_{job['id']}"):
                    details = get_job_details(job['id'])
                    if details:
                        st.json(details)
    else:
        st.info("No jobs found")


elif page == "🤖 Auto Monitoring":
    st.markdown('<div class="main-header">🤖 Auto Monitoring</div>', unsafe_allow_html=True)
    
    # Get monitoring status
    status = get_monitoring_status()
    
    if status:
        # System status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_icon = "🟢" if status['enabled'] else "🔴"
            st.metric("System Status", f"{status_icon} {'Running' if status['enabled'] else 'Stopped'}")
        with col2:
            st.metric("Monitored Accounts", len(status['accounts']))
        with col3:
            st.metric("Check Interval", f"{status['check_interval_minutes']} min")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2 = st.tabs(["📋 Monitored Accounts", "➕ Add Account"])
    
    with tab1:
        st.subheader("Monitored Accounts")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("💡 النظام يراقب الحسابات تلقائياً ويحمل الفيديوهات الجديدة فقط")
        with col2:
            if st.button("🔄 Refresh", key="refresh_monitoring"):
                st.rerun()
            if st.button("⚡ Check Now", key="check_now"):
                with st.spinner("Triggering check..."):
                    result = trigger_check_now()
                    if result:
                        st.success("✅ Check cycle started!")
        
        # Get monitored accounts from database
        try:
            import sys
            sys.path.append('.')
            from sqlalchemy import select
            from app.models.database import get_db
            from app.models.models import MonitoredAccount
            import asyncio
            
            async def get_accounts_data():
                try:
                    async for db in get_db():
                        result = await db.execute(
                            select(MonitoredAccount).where(MonitoredAccount.enabled == True)
                        )
                        return result.scalars().all()
                except Exception as e:
                    # Table doesn't exist
                    return None
            
            accounts = asyncio.run(get_accounts_data())
            
            if accounts is None:
                st.error("⚠️ Auto Monitoring table not found!")
                st.info("""
                **To fix this issue:**
                Click the button below to initialize the database tables.
                """)
                
                if st.button("🔧 Initialize Database Tables", type="primary"):
                    with st.spinner("Initializing database..."):
                        try:
                            response = requests.post(f"{API_BASE_URL}/database/init")
                            if response.status_code == 200:
                                st.success("✅ Database initialized successfully!")
                                st.balloons()
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"❌ Error: {response.text}")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                
                st.markdown("---")
                st.write("**Or manually:**")
                st.code("POST https://tiktok-scraper-api-ulzl.onrender.com/api/v1/database/init")
            elif accounts:
                for account in accounts:
                    status_icon = "✅" if account.enabled else "⏸️"
                    
                    with st.expander(
                        f"{status_icon} @{account.username} - {account.total_new_videos} videos found",
                        expanded=True
                    ):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Checks", account.total_checks)
                            st.write(f"**Username:** @{account.username}")
                        
                        with col2:
                            st.metric("New Videos", account.total_new_videos)
                            if account.last_video_id:
                                st.write(f"**Last Video ID:** {account.last_video_id[:15]}...")
                        
                        with col3:
                            st.metric("Check Interval", f"{account.check_interval_minutes} min")
                            if account.last_check_at:
                                from datetime import datetime
                                time_diff = datetime.utcnow() - account.last_check_at
                                minutes_ago = int(time_diff.total_seconds() / 60)
                                st.write(f"**Last Check:** {minutes_ago} min ago")
                        
                        with col4:
                            if account.last_new_video_at:
                                time_diff = datetime.utcnow() - account.last_new_video_at
                                hours_ago = int(time_diff.total_seconds() / 3600)
                                st.metric("Last New Video", f"{hours_ago}h ago")
                            else:
                                st.metric("Last New Video", "Never")
                        
                        # Progress bar
                        if account.total_checks > 0:
                            success_rate = (account.total_new_videos / account.total_checks) * 100
                            st.progress(success_rate / 100, text=f"Success Rate: {success_rate:.1f}%")
                        
                        # Remove button
                        if st.button(f"🗑️ Remove", key=f"remove_{account.username}"):
                            result = remove_monitored_account(account.username)
                            if result:
                                st.success(f"✅ Removed @{account.username}")
                                st.rerun()
            else:
                st.info("📭 No monitored accounts. Add one below!")
                
        except Exception as e:
            st.error(f"Error loading accounts: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    with tab2:
        st.subheader("Add Account to Monitoring")
        
        st.info("""
        **كيف يعمل؟**
        1. يحمل آخر فيديو فوراً عند الإضافة
        2. يفحص الحساب كل ساعة (أو المدة المحددة)
        3. إذا وجد فيديو جديد → يحمله ويرفعه على Google Drive
        4. إذا لا يوجد جديد → ينتظر ويفحص مرة أخرى
        """)
        
        with st.form("add_monitoring_form"):
            username = st.text_input(
                "Username",
                placeholder="mikaylanogueira",
                help="Enter username without @"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                check_interval = st.number_input(
                    "Check Interval (minutes)",
                    min_value=15,
                    max_value=1440,
                    value=60,
                    help="How often to check for new videos"
                )
            
            with col2:
                st.write("")
                st.write("")
                st.write("**Recommended:**")
                st.write("- Active accounts: 30 min")
                st.write("- Normal accounts: 60 min")
                st.write("- Slow accounts: 180 min")
            
            submitted = st.form_submit_button("➕ Add to Monitoring", type="primary")
            
            if submitted:
                if not username:
                    st.error("Please enter a username")
                else:
                    with st.spinner(f"Adding @{username} and downloading latest video..."):
                        result = add_monitored_account(username)
                        
                        if result and result.get('success'):
                            st.success(f"✅ Added @{username} to monitoring!")
                            st.success("📥 Latest video is being downloaded now...")
                            st.balloons()
                            time.sleep(2)
                            st.rerun()


elif page == "🎬 Videos":
    st.markdown('<div class="main-header">🎬 Videos</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        mode_filter = st.selectbox("Filter by Mode", ["All", "profile", "hashtag"])
    
    with col2:
        value_filter = st.text_input("Filter by Value", placeholder="username or hashtag")
    
    with col3:
        limit = st.number_input("Limit", min_value=10, max_value=200, value=50)
    
    # Get videos
    videos_data = get_videos(
        mode=None if mode_filter == "All" else mode_filter,
        value=value_filter or None,
        limit=limit
    )
    
    st.write(f"**Total Videos:** {videos_data['total']}")
    
    if videos_data['videos']:
        videos_list = []
        for video in videos_data['videos']:
            status_emoji = {
                "pending": "⏳",
                "downloading": "⬇️",
                "downloaded": "💾",
                "uploading": "⬆️",
                "uploaded": "✅",
                "failed": "❌"
            }.get(video['status'], "❓")
            
            videos_list.append({
                "Status": f"{status_emoji} {video['status']}",
                "Video ID": video['id'],
                "Author": video['author_username'],
                "Views": f"{video['views']:,}",
                "Likes": f"{video['likes']:,}",
                "Size": f"{video['file_size'] / (1024**2):.2f} MB" if video['file_size'] else "N/A",
                "Watermark": "❌" if video['has_watermark'] else "✅",
                "Drive": "✅" if video['drive_file_id'] else "❌",
                "URL": video['url']
            })
        
        df = pd.DataFrame(videos_list)
        st.dataframe(df, use_container_width=True)
        
        # Download section
        st.markdown("---")
        st.subheader("📥 Download Videos")
        
        for video in videos_data['videos']:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{video['author_username']}** - {video['id']}")
            
            with col2:
                if video['drive_file_id']:
                    drive_link = f"https://drive.google.com/file/d/{video['drive_file_id']}/view"
                    st.link_button("🔗 Drive", drive_link)
            
            with col3:
                if st.button(f"💾 Download", key=f"download_{video['id']}"):
                    try:
                        download_url = f"{API_BASE_URL}/videos/{video['id']}/download"
                        response = requests.get(download_url, stream=True)
                        
                        if response.status_code == 200:
                            filename = f"{video['author_username']}_{video['id']}.mp4"
                            
                            # Create download button
                            st.download_button(
                                label="⬇️ Save File",
                                data=response.content,
                                file_name=filename,
                                mime="video/mp4",
                                key=f"save_{video['id']}"
                            )
                        else:
                            st.error("Video not available for download")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    else:
        st.info("No videos found")


elif page == "⏰ Scheduled Jobs":
    st.markdown('<div class="main-header">⏰ Scheduled Jobs</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 View Scheduled Jobs", "➕ Create Scheduled Job"])
    
    with tab1:
        scheduled_jobs = get_scheduled_jobs()
        
        if scheduled_jobs:
            for job in scheduled_jobs:
                status_icon = "✅" if job['enabled'] else "⏸️"
                
                with st.expander(f"{status_icon} {job['name']} - Every {job['interval_minutes']} min"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Name:** {job['name']}")
                        st.write(f"**Mode:** {job['mode']}")
                        st.write(f"**Value:** {job['value']}")
                        st.write(f"**Enabled:** {'Yes' if job['enabled'] else 'No'}")
                    
                    with col2:
                        st.write(f"**Interval:** {job['interval_minutes']} minutes")
                        st.write(f"**Limit:** {job['limit']}")
                        st.write(f"**No Watermark:** {'Yes' if job['no_watermark'] else 'No'}")
                    
                    with col3:
                        st.write(f"**Total Runs:** {job['total_runs']}")
                        st.write(f"**Successful:** {job['successful_runs']}")
                        st.write(f"**Failed:** {job['failed_runs']}")
                        if job['last_run_at']:
                            st.write(f"**Last Run:** {job['last_run_at'][:19]}")
        else:
            st.info("No scheduled jobs found")
    
    with tab2:
        with st.form("create_scheduled_job_form"):
            name = st.text_input("Job Name", placeholder="Daily Scrape - @username")
            
            col1, col2 = st.columns(2)
            
            with col1:
                mode = st.selectbox("Mode", ["profile", "hashtag"], key="sched_mode")
                value = st.text_input("Username / Hashtag", key="sched_value")
            
            with col2:
                limit = st.number_input("Videos per Run", min_value=1, max_value=200, value=50, key="sched_limit")
                interval = st.number_input("Interval (minutes)", min_value=5, max_value=10080, value=60)
            
            no_watermark = st.checkbox("Download without watermark", value=True, key="sched_nowm")
            
            submitted = st.form_submit_button("Create Scheduled Job", type="primary")
            
            if submitted:
                if not name or not value:
                    st.error("Please fill in all required fields")
                else:
                    with st.spinner("Creating scheduled job..."):
                        job = create_scheduled_job(name, mode, value, limit, interval, no_watermark)
                        
                        if job:
                            st.success(f"✅ Scheduled job created successfully!")
                            st.json(job)


elif page == "⚙️ Settings":
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    st.subheader("🔐 Google Drive Configuration")
    
    st.info("""
    **How to get Google Drive credentials:**
    1. Go to [Google Cloud Console](https://console.cloud.google.com/)
    2. Create a new project or select existing
    3. Enable Google Drive API
    4. Create OAuth 2.0 credentials
    5. Download credentials.json
    6. Paste the content below
    """)
    
    with st.form("google_drive_settings"):
        st.write("### Google Drive Credentials")
        
        credentials_json = st.text_area(
            "Credentials JSON",
            height=200,
            placeholder='Paste your credentials.json content here',
            help="Paste the entire content of your downloaded credentials.json file"
        )
        
        folder_id = st.text_input(
            "Default Google Drive Folder ID",
            placeholder="1eJ0IpGpy7KrHkh_157n-qBM04WQCCDc_",
            help="The folder ID where videos will be uploaded by default"
        )
        
        st.markdown("---")
        st.write("### Subtitle Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_subtitles = st.checkbox(
                "Enable Subtitle Generation",
                value=False,
                help="Automatically generate Arabic subtitles for videos"
            )
        
        with col2:
            subtitle_language = st.selectbox(
                "Subtitle Language",
                ["Arabic", "English", "Both"],
                help="Language for subtitle generation"
            )
        
        submitted = st.form_submit_button("💾 Save Settings", type="primary")
        
        if submitted:
            if credentials_json:
                try:
                    import json
                    import base64
                    
                    # Validate JSON
                    creds_data = json.loads(credentials_json)
                    
                    # Save to file
                    with open("credentials/credentials.json", "w") as f:
                        json.dump(creds_data, f, indent=2)
                    
                    # Also save as base64 for cloud deployment
                    creds_b64 = base64.b64encode(credentials_json.encode()).decode()
                    
                    # Save to .env file
                    env_content = f"""
GOOGLE_DRIVE_CREDENTIALS_BASE64={creds_b64}
GOOGLE_DRIVE_ROOT_FOLDER_ID={folder_id}
ENABLE_SUBTITLES={enable_subtitles}
SUBTITLE_LANGUAGE={subtitle_language}
"""
                    
                    with open(".env", "a") as f:
                        f.write(env_content)
                    
                    st.success("✅ Settings saved successfully!")
                    st.success("🔄 Please restart the application for changes to take effect")
                    
                    st.code(f"""
Credentials saved to: credentials/credentials.json
Folder ID: {folder_id}
Subtitles: {'Enabled' if enable_subtitles else 'Disabled'}
Language: {subtitle_language}
""")
                    
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON format. Please check your credentials.")
                except Exception as e:
                    st.error(f"❌ Error saving settings: {str(e)}")
            else:
                st.warning("⚠️ Please paste your credentials JSON")
    
    st.markdown("---")
    
    st.subheader("📊 Current Configuration")
    
    try:
        import os
        from pathlib import Path
        
        creds_file = Path("credentials/credentials.json")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Credentials File", "✅ Exists" if creds_file.exists() else "❌ Missing")
            st.metric("API URL", API_BASE_URL)
        
        with col2:
            env_folder_id = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER_ID", "Not set")
            st.metric("Folder ID", env_folder_id)
            st.metric("Subtitles", os.getenv("ENABLE_SUBTITLES", "Disabled"))
        
        if creds_file.exists():
            st.success("✅ Google Drive is configured")
            
            with st.expander("View Credentials"):
                with open(creds_file, "r") as f:
                    creds_content = f.read()
                st.code(creds_content, language="json")
        else:
            st.warning("⚠️ Google Drive credentials not found. Please configure above.")
    
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
