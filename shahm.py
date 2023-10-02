import os
import json
import aiohttp
import asyncio
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, Filters

ENTER_API_KEY = 1
ENTER_ENV_VARS = 2
INSTALL_BUILDPACKS = 3
DEPLOY_APP = 4
SEND_TXT_FILE = 5

user_env_vars = {}

TELEGRAM_TOKEN = '5970239537:AAF8OqpJ8kZMNXyZcfnCuJwQ0ZalW_KZ4DA'
HEROKU_APP_NAME = 'jokeruserbot'

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("مرحبًا! من فضلك أرسل مفتاح Heroku API الخاص بك.")
    return ENTER_API_KEY

async def enter_api_key(update: Update, context: CallbackContext):
    api_key = update.message.text.strip()
    os.environ['HEROKU_API_KEY'] = api_key

    try:
        await update.message.reply_text(f'تم قبول مفتاح Heroku API. سيتم الآن بدء عملية النشر.')

        github_url = 'https://github.com/lml10l/test/tarball/HuRe/'
        async with aiohttp.ClientSession() as session:
            async with session.get(github_url) as response:
                if response.status == 200:
                    content = await response.text()
                    if 'app.json' in content:
                        await update.message.reply_text(f'تم العثور على ملف app.json. جارٍ جلب متغيرات البيئة...')
                        
                        app_json_url = github_url.replace('/tarball/', '/tree/')
                        async with session.get(app_json_url + 'app.json') as app_json_response:
                            app_json_content = await app_json_response.text()
                            try:
                                app_json_data = json.loads(app_json_content)
                                env_vars = app_json_data.get('env', {})
                                for var_name, var_value in env_vars.items():
                                    user_env_vars[var_name] = None

                                env_var_names = "\n".join(user_env_vars.keys())
                                await update.message.reply_text(
                                    f'المتغيرات المطلوبة:\n{env_var_names}\n\nمن فضلك أرسل قيم المتغيرات واحدة تلو الأخرى.'
                                )
                                return ENTER_ENV_VARS

                            except Exception as e:
                                await update.message.reply_text(f'خطأ في تحليل ملف app.json: {str(e)}')

                    else:
                        await update.message.reply_text('خطأ: لم يتم العثور على ملف app.json في الرابط المقدم.')

                else:
                    await update.message.reply_text('خطأ في جلب الملفات من GitHub.')

    except Exception as e:
        await update.message.reply_text(f'خطأ في التحقق من مفتاح Heroku API أو بدء عملية النشر. من فضلك حاول مرة أخرى.')
        return ConversationHandler.END

async def enter_env_vars(update: Update, context: CallbackContext):
    var_name = list(user_env_vars.keys())[0]
    user_env_vars[var_name] = update.message.text.strip()

    if user_env_vars[var_name]:
        user_env_vars.pop(var_name)

    if user_env_vars:
        var_name = list(user_env_vars.keys())[0]
        await update.message.reply_text(
            f'تم تعبئة {var_name}. الرجاء إرسال القيمة التالية لـ {var_name}.'
        )
    else:
        await update.message.reply_text('تم تعبئة جميع المتغيرات بنجاح. جارٍ بدء تنصيب buildpacks...')
        await install_buildpacks(update.message.chat_id)
        return INSTALL_BUILDPACKS

async def install_buildpacks(chat_id):
    try:
        github_url = 'https://github.com/lml10l/test/tarball/HuRe/'
        async with aiohttp.ClientSession() as session:
            async with session.get(github_url + 'app.json') as app_json_response:
                app_json_data = json.loads(await app_json_response.text())
                buildpacks = app_json_data.get('buildpacks', [])

                for buildpack in buildpacks:
                    os.system(f'heroku buildpacks:add {buildpack["url"]} --app {HEROKU_APP_NAME}')

                await update.message.reply_text(f'تم تنصيب جميع buildpacks بنجاح.')
                await deploy_app(chat_id)
                return DEPLOY_APP

    except Exception as e:
        await update.message.reply_text(f'خطأ في تنصيب buildpacks. من فضلك حاول مرة أخرى.')
        return ConversationHandler.END

async def deploy_app(chat_id):
    try:
        os.system(f'git push heroku master --app {HEROKU_APP_NAME}')
        await update.message.reply_text(f'تم بدء عملية النشر على Heroku لتطبيق {HEROKU_APP_NAME}.')
        await update.message.reply_text(f'يرجى الانتظار حتى يتم نشر التطبيق بنجاح...')
    except Exception as e:
        await update.message.reply_text(f'خطأ في بدء عملية النشر. من فضلك حاول مرة أخرى.')
        return ConversationHandler.END

async def send_txt_file(update: Update, context: CallbackContext):
    txt_file_content = "تم نشر التطبيق بنجاح!"
    with open("deployed_app.txt", "w") as file:
        file.write(txt_file_content)

    await update.message.reply_text("تم نشر التطبيق بنجاح. إليك ملف نصي:")
    await update.message.reply_document(document=InputFile('deployed_app.txt'))

    return ConversationHandler.END

async def main():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ENTER_API_KEY: [MessageHandler(Filters.text & ~Filters.command, enter_api_key)],
            ENTER_ENV_VARS: [MessageHandler(Filters.text & ~Filters.command, enter_env_vars)],
            INSTALL_BUILDPACKS: [MessageHandler(Filters.text & ~Filters.command, install_buildpacks)],
            DEPLOY_APP: [MessageHandler(Filters.text & ~Filters.command, send_txt_file)],
        },
        fallbacks=[]
    )

    dispatcher.add_handler(conv_handler)
    await updater.start_polling()
    await updater.idle()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())