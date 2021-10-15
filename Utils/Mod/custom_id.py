from Utils.Configuration import config


def custom_id(view: str, role_id: int) -> str:
    """create a custom id from the bot name : the view : the identifier"""
    return f"{config.BOT_NAME}:{view}:{role_id}"
