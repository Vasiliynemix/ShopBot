COMMAND_HELP: dict[str, str] = {
    'help_admin': '''<b>функции админа</b>
- Для того, чтобы посмотреть список модераторов используйте команду /moderators
- Чтобы удалить модератора нажмите на соответствующую кнопку в меню
- Чтобы добавить модератора нажмите "Добавить модератора"\n
<b>функции модератора</b>
- Какие-то функции модератора\n
<b>функции пользователя</b>
- Какие-то функции пользователя
    ''',
    'help_moderator': '''<b>функции модератора</b>
- Какие-то функции\n
<b>функции пользователя</b>
- Какие-то функции пользователя
    ''',
    'help_user': '''<b>функции пользователя</b>
- Какие-то функции пользователя
    ''',
}

LEXICON_COMMANDS: dict[str, str] = {
    '/help': 'Помощь работы с ботом',
}


async def create_text_product(name, description, price, volume, category=None):
    if int(volume) > 0:
        is_volume = 'да'
    else:
        is_volume = 'нет'

    if category:
        text = (
            f'название: {name}\n'
            f'описание: {description}\n'
            f'цена: {price}\n'
            f'в наличии: {is_volume}\n'
            f'категория: {category}'
        )
    else:
        text = (
            f'название: {name}\n'
            f'описание: {description}\n'
            f'цена: {price}\n'
            f'в наличии: {is_volume}'
        )

    return text
