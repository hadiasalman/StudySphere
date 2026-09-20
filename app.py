# ==========================================
# GOOGLE AUTHENTICATION
# ==========================================

is_logged_in = getattr(st.user, "is_logged_in", False)

if not is_logged_in:

    st.markdown(
        """
        <style>

        .login-container {
            max-width: 650px;
            margin: 100px auto 30px auto;
            text-align: center;
            padding: 50px;
            border-radius: 25px;
            background: white;
            box-shadow: 0 10px 40px rgba(0,0,0,0.10);
        }

        .login-title {
            font-size: 42px;
            font-weight: 800;
            color: #0F172A;
        }

        .login-subtitle {
            font-size: 17px;
            color: #64748B;
            margin-top: 10px;
            margin-bottom: 30px;
        }

        div.stButton > button {
            background: #14B8A6 !important;
            color: white !important;
            border: 1px solid #0F766E !important;
            border-radius: 11px;
            min-height: 48px;
            font-weight: 700;
        }

        div.stButton > button:hover {
            background: #0F766E !important;
            color: white !important;
        }

        </style>

        <div class="login-container">

        <div class="login-title">
        🎓 StudySphere
        </div>

        <div class="login-subtitle">
        Learn smarter. Plan better. Achieve more.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.button(
        "🔐 Continue with Google",
        on_click=st.login,
        use_container_width=True
    )

    st.stop()
