import os
import asyncio
import logging
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import Forbidden

# Configuração de Logs para ver o que se passa no painel do Render
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- MENSAGENS DO BOT ---
WELCOME_MSG = """*Bem-vindo ao Nuno Morais Apostas – o seu companheiro de confiança para dicas de apostas inteligentes e responsáveis.

O nosso foco são sugestões desportivas claras e com alta probabilidade de acerto para o ajudar a jogar com mais confiança.

🔞 Apenas para maiores de 18 anos.

O que vai encontrar:

· Palpites diários bem pesquisados
· Odds sólidas e com bom valor
· Atualizações ao vivo à medida que a ação acontece
· Dicas simples de gestão de banca e estratégias de apostas
· Conteúdo extra exclusivo para os nossos subscritores"""

JOIN_LINK_MSG = """👇 Clique aqui para entrar no nosso canal de Telegram: 
https://t.me/nun0moraised4N76nm"""

SUPPORT_MSG = """Precisa de ajuda?

Entre em contacto:
📩 @NUNO_MORAlS

Responderei o mais breve possível."""

# --- LINKS DAS IMAGENS (Substitua por os links do seu GitHub) ---
# DICA: No GitHub, abra a imagem, clique com o botão direito e escolha "Copiar endereço da imagem".
# O link deve terminar em .jpg ou .png e vir normalmente do domínio 'raw.githubusercontent.com'
IMAGE_URL_1 = "https://raw.githubusercontent.com/nome-de-utilizador/repositorio/main/prova1.jpg"
IMAGE_URL_2 = "https://raw.githubusercontent.com/nome-de-utilizador/repositorio/main/prova2.jpg"
IMAGE_URL_3 = "https://raw.githubusercontent.com/nome-de-utilizador/repositorio/main/prova3.jpg"
IMAGE_URL_4 = "https://raw.githubusercontent.com/nome-de-utilizador/repositorio/main/prova4.jpg"

# Registo de utilizadores que já têm o ciclo de 6 horas ativo
active_users = set()

async def send_sequence(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Envia a sequência completa de mensagens e imagens."""
    try:
        # 1. Mensagem de Boas-vindas
        await context.bot.send_message(chat_id=chat_id, text=WELCOME_MSG)
        
        # 2. Esperar 2 segundos
        await asyncio.sleep(2)
        
        # 3. Link do Canal
        await context.bot.send_message(chat_id=chat_id, text=JOIN_LINK_MSG)
        
        # 4. Esperar 2 segundos
        await asyncio.sleep(2)
        
        # 5. Enviar 4 imagens de prova (Agrupadas como um álbum para não enviar spam de notificações)
        media_group = [
            InputMediaPhoto(IMAGE_URL_1),
            InputMediaPhoto(IMAGE_URL_2),
            InputMediaPhoto(IMAGE_URL_3),
            InputMediaPhoto(IMAGE_URL_4)
        ]
        try:
            await context.bot.send_media_group(chat_id=chat_id, media=media_group)
        except Exception as e:
            logger.warning(f"Não foi possível enviar as imagens (verifique os links do GitHub): {e}")
            await context.bot.send_message(
                chat_id=chat_id, 
                text="[As imagens de prova aparecerão aqui assim que os links do GitHub forem configurados no código]"
            )
            
        # 6. Link do Canal (Novamente)
        await context.bot.send_message(chat_id=chat_id, text=JOIN_LINK_MSG)
        
        # 7. Esperar 5 segundos
        await asyncio.sleep(5)
        
        # 8. Mensagem de Ajuda
        await context.bot.send_message(chat_id=chat_id, text=SUPPORT_MSG)
        
    except Forbidden:
        # O utilizador bloqueou o bot
        logger.info(f"O utilizador {chat_id} bloqueou o bot.")
        raise  # Passa o erro para parar o ciclo
    except Exception as e:
        logger.error(f"Erro ao enviar sequência para {chat_id}: {e}")

async def user_loop(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Gere o ciclo que repete a sequência a cada 6 horas."""
    while True:
        try:
            await send_sequence(chat_id, context)
            
            # Esperar 6 horas (6 horas * 60 minutos * 60 segundos = 21600 segundos)
            # await asyncio.sleep(21600) 
            # Dica: Para testar se o ciclo funciona, altere temporariamente para 60 segundos
            await asyncio.sleep(21600)
            
        except Forbidden:
            # Se bloquear o bot, retira da lista ativa e quebra o ciclo
            if chat_id in active_users:
                active_users.remove(chat_id)
            break
        except Exception as e:
            logger.error(f"Erro no ciclo do utilizador {chat_id}: {e}")
            await asyncio.sleep(60) # Espera 1 minuto antes de tentar novamente em caso de erro

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /start e inicia o ciclo do utilizador."""
    chat_id = update.effective_chat.id
    
    if chat_id not in active_users:
        active_users.add(chat_id)
        logger.info(f"Nova subscrição iniciada: Utilizador {chat_id}")
        
        # Inicia a tarefa em segundo plano para este utilizador específico
        context.application.create_task(user_loop(chat_id, context))
    else:
        # Se o utilizador já clicou no start antes e o ciclo já está a correr
        await update.message.reply_text("Olá! As tuas atualizações já estão ativas e a ser enviadas regularmente. ⏳")

def main():
    """Inicia o Bot."""
    # O Token do bot deve ser colocado nas variáveis de ambiente do Render (Environment Variables)
    TOKEN = os.environ.get("BOT_TOKEN")
    
    if not TOKEN:
        logger.error("ERRO: BOT_TOKEN não encontrado. Configure a variável de ambiente no Render.")
        return

    # Cria a Aplicação
    application = Application.builder().token(TOKEN).build()

    # Adiciona o comando /start
    application.add_handler(CommandHandler("start", start))

    # Inicia o bot
    logger.info("Bot iniciado e a aguardar mensagens...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
