import os
import asyncio
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIGURAÇÃO DO GITHUB ---
GITHUB_BASE_URL = "https://raw.githubusercontent.com/chancellorlono-afk/whatappfootballportugues/main/"

# Nomes exatos dos ficheiros da sua imagem (com os espaços codificados como %20)
IMAGE_URLS = [
    f"{GITHUB_BASE_URL}PHOTO-2026-06-16-19-19-44.jpg",
    f"{GITHUB_BASE_URL}PHOTO-2026-06-16-19-19-43.jpg",
    f"{GITHUB_BASE_URL}PHOTO-2026-06-16-19-19-43%203.jpg",
    f"{GITHUB_BASE_URL}PHOTO-2026-06-16-19-19-43%202.jpg"
]

async def send_sequence(context: ContextTypes.DEFAULT_TYPE):
    """Esta função executa a sequência inteira e será chamada a cada 6 horas."""
    chat_id = context.job.chat_id

    # 1. Enviar mensagem de boas-vindas
    welcome_msg = (
        "*Bem-vindo ao Nuno Morais Apostas – o seu companheiro de confiança para dicas de apostas inteligentes e responsáveis.*\n\n"
        "O nosso foco são sugestões desportivas claras e com alta probabilidade de acerto para o ajudar a jogar com mais confiança.\n\n"
        "🔞 Apenas para maiores de 18 anos.\n\n"
        "O que vai encontrar:\n"
        "· Palpites diários bem pesquisados\n"
        "· Odds sólidas e com bom valor\n"
        "· Atualizações ao vivo à medida que a ação acontece\n"
        "· Dicas simples de gestão de banca e estratégias de apostas\n"
        "· Conteúdo extra exclusivo para os nossos subscritores"
    )
    await context.bot.send_message(chat_id=chat_id, text=welcome_msg, parse_mode='Markdown')

    # Esperar 2 segundos
    await asyncio.sleep(2)

    # 2. Enviar o link do canal
    link_msg = (
        "👇 Clique aqui para entrar no nosso canal de Telegram:\n"
        "https://t.me/nun0moraised4N76nm"
    )
    await context.bot.send_message(chat_id=chat_id, text=link_msg)

    # Esperar 2 segundos
    await asyncio.sleep(2)

    # 3. Enviar as 4 imagens de prova como um álbum
    try:
        media_group = [InputMediaPhoto(media=url) for url in IMAGE_URLS]
        await context.bot.send_media_group(chat_id=chat_id, media=media_group)
    except Exception as e:
        print(f"Erro ao enviar imagens (verifique se a URL do GitHub está correta): {e}")
        # Agora o bot avisa no chat caso falhe o download das imagens
        error_msg = "⚠️ *Aviso do Sistema:* As imagens falharam a carregar. Verifique se configurou a URL do GitHub no código."
        await context.bot.send_message(chat_id=chat_id, text=error_msg, parse_mode='Markdown')

    # 4. Enviar o link do canal de novo
    await context.bot.send_message(chat_id=chat_id, text=link_msg)

    # Esperar 5 segundos
    await asyncio.sleep(5)

    # 5. Enviar a mensagem de ajuda
    help_msg = (
        "Precisa de ajuda?\n\n"
        "Entre em contacto:\n"
        "📩 @NUNO_MORAlS\n\n"
        "Responderei o mais breve possível."
    )
    await context.bot.send_message(chat_id=chat_id, text=help_msg)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gere o comando /start e inicia o ciclo para o utilizador."""
    chat_id = update.effective_chat.id
    
    # Parar trabalhos anteriores deste utilizador para evitar envio duplicado se ele fizer /start 2 vezes
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()

    # Iniciar um trabalho repetitivo. 
    # interval=21600 (6 horas em segundos: 6 * 60 * 60)
    # first=0 (executa a primeira vez de imediato)
    context.job_queue.run_repeating(
        send_sequence, 
        interval=21600, 
        first=0, 
        chat_id=chat_id, 
        name=str(chat_id)
    )

def main():
    # O Render vai fornecer o BOT_TOKEN pelas Environment Variables
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("ERRO: A variável de ambiente BOT_TOKEN não foi definida!")
        return

    # Iniciar a aplicação do Bot
    application = Application.builder().token(token).build()
    
    # Adicionar o handler do comando /start
    application.add_handler(CommandHandler("start", start))
    
    print("O Bot está a correr...")
    application.run_polling()

if __name__ == '__main__':
    main()
