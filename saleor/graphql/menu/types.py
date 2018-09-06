import graphene
from graphene import relay

from ...menu import models
from ..core.types.common import CountableDjangoObjectType


class Menu(CountableDjangoObjectType):
    class Meta:
        description = """Represents a single menu - an object that is used
        to help navigate through the store."""
        interfaces = [relay.Node]
        exclude_fields = ['json_content']
        model = models.Menu

    def resolve_items(self, info, **kwargs):
        return self.items.filter(level=0).select_related(
            'category', 'collection', 'page')


class MenuItem(CountableDjangoObjectType):
    url = graphene.String(description='URL to the menu item.')

    class Meta:
        description = """Represents a single item of the related menu.
        Can store categories, collection or pages."""
        interfaces = [relay.Node]
        only_fields = ['children', 'id', 'menu', 'name', 'url']
        model = models.MenuItem
