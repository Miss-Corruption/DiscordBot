import disnake

__all__ = (
    "accept_mark",
    "deny_mark",
    "choice_marks",
)


def _partial(name: str, id: int, animated: bool = False):
    name = str(name)
    id = int(id)
    return disnake.PartialEmoji(name=name, id=id, animated=animated)


accept_mark = _partial("accept_mark", 892770746013724683)
deny_mark = _partial("deny_mark", 892770746034704384)
choice_marks = (accept_mark, deny_mark)
