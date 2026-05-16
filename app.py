import streamlit as st
from database import supabase
from auth import login_player, create_player, list_players


st.set_page_config(
    page_title="EntreVersículos",
    page_icon="📖",
    layout="wide"
)


def init_session():
    if "user" not in st.session_state:
        st.session_state.user = None


def logout():
    st.session_state.user = None
    st.rerun()


def login_screen():
    st.title("📖 EntreVersículos")
    st.subheader("Um jogo de leitura, reflexão e partilha bíblica.")

    with st.form("login_form"):
        name = st.text_input("Nome")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

    if submitted:
        user = login_player(name, password)

        if user:
            st.session_state.user = user
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Nome ou senha incorretos.")


def admin_panel():
    st.header("👑 Painel do Admin")

    tab1, tab2, tab3 = st.tabs([
        "Cadastrar jogador",
        "Jogadores",
        "Temas cadastrados"
    ])

    with tab1:
        st.subheader("Cadastrar novo jogador")

        with st.form("create_player_form"):
            name = st.text_input("Nome do jogador")
            password = st.text_input("Senha", type="password")
            is_admin = st.checkbox("É administrador?")
            submitted = st.form_submit_button("Cadastrar")

        if submitted:
            if not name or not password:
                st.warning("Preencha nome e senha.")
            else:
                try:
                    create_player(name, password, is_admin)
                    st.success("Jogador cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao cadastrar jogador: {e}")

    with tab2:
        st.subheader("Jogadores cadastrados")

        players = list_players()

        if players:
            st.dataframe(players, use_container_width=True)
        else:
            st.info("Nenhum jogador cadastrado.")

    with tab3:
        show_themes()


def create_theme_screen():
    st.header("➕ Cadastrar tema para sessão")

    with st.form("theme_form"):
        theme = st.text_input("Tema")
        description = st.text_area("Descrição")
        verses = st.text_area("Versículos")
        questions = st.text_area("Perguntas")

        submitted = st.form_submit_button("Salvar tema")

    if submitted:
        if not theme:
            st.warning("O campo Tema é obrigatório.")
            return

        user = st.session_state.user

        response = (
            supabase.table("session_themes")
            .insert({
                "theme": theme,
                "description": description,
                "verses": verses,
                "questions": questions,
                "created_by": user["id"]
            })
            .execute()
        )

        if response.data:
            st.success("Tema cadastrado com sucesso!")
        else:
            st.error("Erro ao cadastrar tema.")


def show_themes():
    st.header("📚 Temas para sessão")

    response = (
        supabase.table("session_themes")
        .select("""
            id,
            theme,
            description,
            verses,
            questions,
            created_at,
            players (
                name
            )
        """)
        .order("created_at", desc=True)
        .execute()
    )

    themes = response.data

    if not themes:
        st.info("Nenhum tema cadastrado ainda.")
        return

    for item in themes:
        author = "Desconhecido"

        if item.get("players"):
            author = item["players"].get("name", "Desconhecido")

        with st.expander(f"📖 {item['theme']}"):
            st.markdown(f"**Descrição:** {item.get('description') or 'Sem descrição'}")
            st.markdown("**Versículos:**")
            st.write(item.get("verses") or "Não informado")

            st.markdown("**Perguntas:**")
            st.write(item.get("questions") or "Não informado")

            st.caption(f"Cadastrado por: {author}")


def player_panel():
    user = st.session_state.user

    st.sidebar.title("📖 EntreVersículos")
    st.sidebar.write(f"Olá, **{user['name']}**")

    menu = st.sidebar.radio(
        "Menu",
        [
            "Ver temas",
            "Cadastrar tema"
        ]
    )

    if st.sidebar.button("Sair"):
        logout()

    if menu == "Ver temas":
        show_themes()

    elif menu == "Cadastrar tema":
        create_theme_screen()


def main():
    init_session()

    if st.session_state.user is None:
        login_screen()
        return

    user = st.session_state.user

    if user.get("is_admin"):
        st.sidebar.title("👑 Admin")
        st.sidebar.write(f"Olá, **{user['name']}**")

        menu = st.sidebar.radio(
            "Menu",
            [
                "Painel Admin",
                "Ver temas",
                "Cadastrar tema"
            ]
        )

        if st.sidebar.button("Sair"):
            logout()

        if menu == "Painel Admin":
            admin_panel()
        elif menu == "Ver temas":
            show_themes()
        elif menu == "Cadastrar tema":
            create_theme_screen()

    else:
        player_panel()

def footer():
    st.markdown(
        """
        <hr>
        <div style='text-align: center; color: gray; font-size: 14px; padding: 10px;'>
            © 2026 EntreVersículos — Desenvolvido por Rufino Panzo
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
    footer()