import functools
import operator
from collections import defaultdict

from django.db.models import Q
from django_filters import OrderingFilter
from django_filters.fields import Lookup
from graphene_django.filter.filterset import Filter

from ...product.filters import SORT_BY_FIELDS
from ...product.models import Product, ProductAttribute
from ..core.filters import DistinctFilterSet
from .fields import AttributeField


class ProductAttributeFilter(Filter):
    field_class = AttributeField

    def filter(self, qs, value):
        if isinstance(value, Lookup):
            value = value.value

        if not value:
            return qs.distinct() if self.distinct else qs

        attributes = ProductAttribute.objects.prefetch_related('values')
        attributes_map = {
            attribute.slug: attribute.pk for attribute in attributes}
        values_map = {
            attr.slug: {value.slug: value.pk for value in attr.values.all()}
            for attr in attributes}
        queries = defaultdict(list)
        # Convert attribute:value pairs into a dictionary where
        # attributes are keys and values are grouped in lists
        for attr_name, val_slug in value:
            if attr_name not in attributes_map:
                raise ValueError('Unknown attribute name: %r' % (attr_name, ))
            attr_pk = attributes_map[attr_name]
            attr_val_pk = values_map[attr_name].get(val_slug, val_slug)
            queries[attr_pk].append(attr_val_pk)
        # Combine filters of the same attribute with OR operator
        # and then combine full query with AND operator.
        combine_and = [
            functools.reduce(
                operator.or_, [
                    Q(**{'variants__attributes__%s' % (key, ): v}) |
                    Q(**{'attributes__%s' % (key, ): v}) for v in values])
            for key, values in queries.items()]
        query = functools.reduce(operator.and_, combine_and)
        qs = self.get_method(qs)(query)
        return qs.distinct() if self.distinct else qs
