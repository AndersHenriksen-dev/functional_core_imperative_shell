{{ fullname | replace('data_handling.', '') }}
{{ "=" * ((fullname | replace('data_handling.', '')) | length) }}

.. automodule:: {{ fullname }}
    :show-inheritance:



{% if classes %}
Classes
-------

.. autosummary::
    :toctree: .
    :nosignatures:
    :template: class

{% for name in classes %}
    {{ fullname }}.{{ name }}
{% endfor %}
{% endif %}

{% if functions %}
Functions
---------

.. autosummary::
    :toctree: .
    :nosignatures:
    :template: function

{% for name in functions %}
    {{ fullname }}.{{ name }}
{% endfor %}
{% endif %}
