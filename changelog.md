# CHANGELOG
## V2.1
This version of BaseApp includes library updates for: 

#### base
* celery (`4.2.0` to `4.4.5`)
* Django (`1.11.29` to `2.2.13`)
* dj-database-url (`0.4.2` to `0.5.0`)
* django-model-utils (`3.1.1` to `4.0.0`)
* django-cors-headers (`3.2.1` to `3.3.0`)
* django-jinja (`2.4.0` to `2.6.0`)
* django-filter (`1.1.0` to `2.3.0`)
* django-crispy-forms (`1.7.0` to `1.9.1`)
* easy-thumbnails (`2.5.0` to `2.7.0`)
* django-fsm (`2.6.0` to `2.7.0`)
* django-phonenumber-field (`2.0.0` to `4.0.0`)
* django-constance[database] (`2.4.0` to `2.6.0`)
* django-picklefield (`2.1.1` to `3.0.1`)
* djmail (`1.0.1` to `2.0.0`)
* djangorestframework (`3.6.3` to `3.11.0`)
* rest-social-auth (`TSL forked version` to `4.2.0`)
* psycopg2 (`2.7.1` to `2.8.5`)
* gunicorn (`19.7.1` to `20.0.4`)
* python-dateutil (`2.6.0` to `2.8.1`)
* phonenumbers (`8.5.0` to `8.12.5`)

#### dev
##### code style
* black (`19.3b0` to `19.10b0`)
* flake8 (`3.7.8` to `3.8.3`)
##### testing
* pytest (`5.2.1` to `5.4.3`)
* pytest-cov (`2.5.1` to `2.10.0`)
* pytest-django (`3.5.1` to `3.9.0`)
* factory-boy (`2.9.2` to `2.12.0`)
* Faker (`4.0.2` to `4.1.0`)
* httpretty (`0.8.14` to `1.0.2`)
#####  helpers
* dj-inmemorystorage (`1.4.1` to `2.1.0`)
##### debug helper / performance monitoring
* django-debug-toolbar (`1.9` to `2.2`)
* django-silk (`2.0.0` to `4.0.1`)
#### live
#####  media/static file storage
* django-storages (`1.7.1` to `1.9.1`)
#####  error logging using sentry
* sentry-sdk (`0.13.0` to `0.13.0`)
#####  flower for celery cluster monitoring
* flower (`0.9.3` to `0.9.4`)
### changes in project(s)
* `base_name` to `basename` @ `router.py`
* `@list_route` to `@action(detail=False)` @`views.py`s
* `@detail_route` to `@action(detail=True)` @`views.py`s
* `import detail_route, list_route` to `import action` @`views.py`s
* `from django.core.urlresolvers import reverse` to `from django.urls import reverse` @ `mixins.py`
### Removed  or deprecated features and Backwards incompatible changes from libraries
#### Django (`1.11.29` to `2.2.13`)
##### 2.2
* Model `Meta.ordering` will no longer affect `GROUP BY` queries.
* `django.utils.timezone.FixedOffset` is deprecated in favor of `datetime.timezone`.
* The undocumented `QuerySetPaginator` alias of `django.core.paginator.Paginator` is deprecated.
* The `FloatRangeField` model and form fields in `django.contrib.postgres` are deprecated in favor of a new name, `DecimalRangeField`, to match the underlying `numrange` data type used in the database.
* The `FILE_CHARSET` setting is deprecated. Starting with Django 3.1, files read from disk must be UTF-8 encoded. Support for overrides that don’t accept it will be removed in Django 3.1.
* `django.contrib.staticfiles.storage.CachedStaticFilesStorage` is deprecated due to the intractable problems that it has. Use `ManifestStaticFilesStorage` or a third-party cloud storage instead.
* `RemoteUserBackend.configure_user()` is now passed `request` as the first positional argument, if it accepts it.
* The `SimpleTestCase.allow_database_queries`, `TransactionTestCase.multi_db`, and `TestCase.multi_db` attributes are deprecated in favor of `SimpleTestCase.databases`, `TransactionTestCase.databases`, and `TestCase.databases`. These new attributes allow databases dependencies to be declared in order to prevent unexpected queries against non-default databases to leak state between tests. The previous behavior of `allow_database_queries=True` and `multi_db=True` can be achieved by setting `databases='__all__'`.
##### 2.1
* To adhere to `PEP 249`, exceptions where a database doesn’t support a feature are changed from `NotImplementedError` to `django.db.NotSupportedError`.
* Renamed the `allow_sliced_subqueries` database feature flag to `allow_sliced_subqueries_with_in`.
* `DatabaseOperations.distinct_sql()` now requires an additional `params` argument and returns a tuple of SQL and parameters instead of a SQL string.
* `DatabaseFeatures.introspected_boolean_field_type` is changed from a method to a property.
* **django.contrib.gis:** Support for SpatiaLite 4.0 is removed.
* **Dropped support for MySQL 5.5:** The end of upstream support for MySQL 5.5 is December 2018. Django 2.1 supports MySQL 5.6 and higher.
* **Dropped support for PostgreSQL 9.3:** The end of upstream support for PostgreSQL 9.3 is September 2018. Django 2.1 supports PostgreSQL 9.4 and higher.
* **Removed BCryptPasswordHasher from the default PASSWORD_HASHERS setting:** if you used `bcrypt` with Django 1.4 or 1.5 (before `BCryptSHA256PasswordHasher` was added in Django 1.6), you might have some passwords that use the `BCryptPasswordHasher` hasher. If you want to continue to allow those passwords to be used, you’ll have to define the `PASSWORD_HASHERS` setting (if you don’t already) and include `'django.contrib.auth.hashers.BCryptPasswordHasher'`.
* **Moved wrap_label widget template context variable:** To fix the lack of `<label>` when using `RadioSelect` and `CheckboxSelectMultiple` with `MultiWidget`, the `wrap_label` context variable now appears as an attribute of each option. For example, in a custom `input_option.html` template, change `{% if wrap_label %}` to `{% if widget.wrap_label %}`.
* **SameSite cookies:** The cookies used for `django.contrib.sessions`, `django.contrib.messages`, and Django’s CSRF protection now set the `SameSite` flag to `Lax` by default. Browsers that respect this flag won’t send these cookies on cross-origin requests. If you rely on the old behavior, set the `SESSION_COOKIE_SAMESITE` and/or `CSRF_COOKIE_SAMESITE` setting to `None`.
* The minimum supported version of `mysqlclient` is increased from 1.3.3 to 1.3.7.
* Support for `SQLite` < 3.7.15 is removed.
* The date format of `Set-Cookie`’s `Expires` directive is changed to follow `RFC 7231#section-7.1.1.1` instead of Netscape’s cookie standard. Hyphens present in dates like `Tue, 25-Dec-2018 22:26:13 GMT` are removed. This change should be merely cosmetic except perhaps for antiquated browsers that don’t parse the new format.
* `allowed_hosts` is now a required argument of private API `django.utils.http.is_safe_url()`.
* The `multiple` attribute rendered by the `SelectMultiple` widget now uses HTML5 boolean syntax rather than XHTML’s `multiple="multiple"`.
* HTML rendered by form widgets no longer includes a closing slash on void elements, e.g. `<br>`. This is incompatible within XHTML, although some widgets already used aspects of HTML5 such as boolean attributes.
* The value of `SelectDateWidget`’s empty options is changed from 0 to an empty string, which mainly may require some adjustments in tests that compare HTML.
* `User.has_usable_password()` and the `is_password_usable()` function no longer return `False` if the password is `None` or an empty string, or if the password uses a hasher that’s not in the `PASSWORD_HASHERS` setting. This undocumented behavior was a regression in Django 1.6 and prevented users with such passwords from requesting a password reset. Audit your code to confirm that your usage of these APIs don’t rely on the old behavior.
* Since migrations are now loaded from `.pyc` files, you might need to delete them if you’re working in a mixed Python 2 and Python 3 environment.
* Using `None` as a `JSONField` lookup value now matches objects that have the specified key and a null value rather than objects that don’t have the key.
* The admin CSS class `field-box` is renamed to `fieldBox` to prevent conflicts with the class given to model fields named “box”.
* Since the admin’s `actions.html`, `change_list_results.html`, `date_hierarchy.html`, `pagination.html`, `prepopulated_fields_js.html`, `search_form.html`, and `submit_line.html` templates can now be overridden per app or per model, you may need to rename existing templates with those names that were written for a different purpose.
* `QuerySet.raw()` now caches its results like regular querysets. Use `iterator()` if you don’t want caching.
* The database router `allow_relation()` method is called in more cases. Improperly written routers may need to be updated accordingly.
* Translations are no longer deactivated before running management commands. If your custom command requires translations to be deactivated (for example, to insert untranslated content into the database), use the new `@no_translations` decorator.
* Management commands no longer allow the abbreviated forms of the `--settings` and `--pythonpath` arguments.
* The private `django.db.models.sql.constants.QUERY_TERMS` constant is removed. The `get_lookup()` and `get_lookups()` methods of the `Lookup Registration API` may be suitable alternatives. Compared to the `QUERY_TERMS` constant, they allow your code to also account for any custom lookups that have been registered.
* Compatibility with `py-bcrypt` is removed as it’s unmaintained. Use `bcrypt` instead.
* The `ForceRHR` GIS function is deprecated in favor of the new `ForcePolygonCW` function.
* `django.utils.http.cookie_date()` is deprecated in favor of `http_date()`, which follows the format of the latest RFC.
* `{% load staticfiles %}` and `{% load admin_static %}` are deprecated in favor of `{% load static %}`, which works the same.
* `django.contrib.staticfiles.templatetags.static()` is deprecated in favor of `django.templatetags.static.static()`.
* Support for `InlineModelAdmin.has_add_permission()` methods that don’t accept `obj` as the second positional argument will be removed in Django 3.0.
* `contrib.auth.views.login()`, `logout()`, `password_change()`, `password_change_done()`, `password_reset()`, `password_reset_done()`, `password_reset_confirm()`, and `password_reset_complete()` are removed.
* The `extra_context` parameter of `contrib.auth.views.logout_then_login()` is removed.
* `django.test.runner.setup_databases()` is removed.
* `django.utils.translation.string_concat()` is removed.
* `django.core.cache.backends.memcached.PyLibMCCache` no longer supports passing `pylibmc` behavior settings as top-level attributes of `OPTIONS`.
* The `host` parameter of `django.utils.http.is_safe_url()` is removed.
* Silencing of exceptions raised while rendering the `{% include %}` template tag is removed.
* `DatabaseIntrospection.get_indexes()` is removed.
* The `authenticate()` method of authentication backends requires `request` as the first positional argument.
* The `django.db.models.permalink()` decorator is removed.
* The `USE_ETAGS` setting is removed. `CommonMiddleware` and `django.utils.cache.patch_response_headers()` no longer set ETags.
* The `Model._meta.has_auto_field attribute` is removed.
* `url()`’s support for inline flags in regular expression groups (`(?i)`, `(?L)`, `(?m)`, `(?s)`, and `(?u)`) is removed.
* Support for `Widget.render()` methods without the `renderer` argument is removed.
##### 2.0
* **Removed support for bytestrings in some places:** For example: `reverse()` now uses `str()` instead of `force_text()` to coerce the `args` and `kwargs` it receives, prior to their placement in the URL. For bytestrings, this creates a string with an undesired b prefix as well as additional quotes (`str(b'foo')` is `b'foo'`). To adapt, call `decode()` on the bytestring before passing it to `reverse()`
* **Database backend API**
    * The `DatabaseOperations.datetime_cast_date_sql()`, `datetime_cast_time_sql()`, `datetime_trunc_sql()`, `datetime_extract_sql()`, and `date_interval_sql()` methods now return only the SQL to perform the operation instead of SQL and a list of parameters.
    * Third-party database backends should add a `DatabaseWrapper.display_name` attribute with the name of the database that your backend works with. Django may use it in various messages, such as in system checks.
    * The first argument of `SchemaEditor._alter_column_type_sql()` is now `model` rather than `table`.
    * The first argument of `SchemaEditor._create_index_name()` is now `table_name` rather than `model`.
    * To enable `FOR UPDATE OF` support, set `DatabaseFeatures.has_select_for_update_of = True`. If the database requires that the arguments to `OF` be columns rather than tables, set `DatabaseFeatures.select_for_update_of_column = True`.
    * To enable support for `Window` expressions, set `DatabaseFeatures.supports_over_clause` to `True`. You may need to customize the `DatabaseOperations.window_start_rows_start_end()` and/or `window_start_range_start_end()` methods.
    * Third-party database backends should add a `DatabaseOperations.cast_char_field_without_max_length` attribute with the database data type that will be used in the `Cast` function for a `CharField` if the `max_length` argument isn’t provided.
    * The first argument of `DatabaseCreation._clone_test_db()` and `get_test_db_clone_settings()` is now `suffix` rather than `number` (in case you want to rename the signatures in your backend for consistency). `django.test` also now passes those values as strings rather than as integers.
    * Third-party database backends should add a `DatabaseIntrospection.get_sequences()` method based on the stub in `BaseDatabaseIntrospection`.
* Dropped support for Oracle 11.2
* Default MySQL isolation level is read committed
* **AbstractUser.last_name max_length increased to 150**
    * A migration for `django.contrib.auth.models.User.last_name` is included. If you have a custom user model inheriting from `AbstractUser`, you’ll need to generate and apply a database migration for your user model.
* **QuerySet.reverse() and last() are prohibited after slicing**
    * Calling `QuerySet.reverse()` or `last()` on a sliced queryset leads to unexpected results due to the slice being applied after reordering.
* Form fields no longer accept optional arguments as positional arguments
* **call_command() validates the options it receives**
    * `call_command()` now validates that the argument parser of the command being called defines all of the options passed to `call_command()`.
* Indexes no longer accept positional arguments
* Foreign key constraints are now enabled on SQLite
    * This will appear as a backwards-incompatible change (`IntegrityError: FOREIGN KEY constraint failed`) if attempting to save an existing model instance that’s violating a foreign key constraint.
* The SessionAuthenticationMiddleware class is removed. It provided no functionality since session authentication is unconditionally enabled in Django 1.10.
* The default HTTP error handlers (`handler404`, etc.) are now callables instead of dotted Python path strings. Django favors callable references since they provide better performance and debugging experience.
* `RedirectView` no longer silences `NoReverseMatch` if the `pattern_name` doesn't exist.
* When `USE_L10N` is off, `FloatField` and `DecimalField` now respect `DECIMAL_SEPARATOR` and `THOUSAND_SEPARATOR` during validation.
* Subclasses of `AbstractBaseUser` are no longer required to implement `get_short_name()` and `get_full_name()`. (The base implementations that raise `NotImplementedError` are removed.) `django.contrib.admin` uses these methods if implemented but doesn’t require them. Third-party apps that use these methods may want to adopt a similar approach.
* The `FIRST_DAY_OF_WEEK` and `NUMBER_GROUPING` format settings are now kept as integers in JavaScript and JSON i18n view outputs.
* `assertNumQueries()` now ignores connection configuration queries. Previously, if a test opened a new database connection, those queries could be included as part of the `assertNumQueries()` count.
* The default size of the Oracle test tablespace is increased from 20M to 50M and the default autoextend size is increased from 10M to 25M.
* To improve performance when streaming large result sets from the database, `QuerySet.iterator()` now fetches 2000 rows at a time instead of 100. The old behavior can be restored using the chunk_size parameter.
* Providing unknown `package` names in the packages argument of the `JavaScriptCatalog` view now raises `ValueError` instead of passing silently.
* A model instance’s primary key now appears in the default `Model.__str__()` method, e.g. `Question object (1)`.
* `makemigrations` now detects changes to the model field `limit_choices_to` option. Add this to your existing migrations or accept an auto-generated migration for fields that use it.
* Performing queries that require automatic spatial transformations now raises `NotImplementedError` on MySQL instead of silently using non-transformed geometries.
* `django.core.exceptions.DjangoRuntimeWarning` is removed. It was only used in the cache backend as an intermediate class in CacheKeyWarning’s inheritance of RuntimeWarning.
* Renamed `BaseExpression._output_field` to `output_field`. You may need to update custom expressions.
* In older versions, forms and formsets combine their `Media` with widget `Media` by concatenating the two. The combining now tries to preserve the relative order of elements in each list. `MediaOrderConflictWarning` is issued if the order can’t be preserved.
* `django.contrib.gis.gdal.OGRException` is removed. It’s been an alias for `GDALException` since Django 1.8.
* Support for GEOS 3.3.x is dropped.
* The way data is selected for `GeometryField` is changed to improve performance, and in raw SQL queries, those fields must now be wrapped in `connection.ops.select`.
* The `context` argument of `Field.from_db_value()` and `Expression.convert_value()` is unused as it’s always an empty dictionary. Support for the old signature in custom fields and expressions remains until `Django 3.0`.
* The `django.db.backends.postgresql_psycopg2` module is deprecated in favor of `django.db.backends.postgresql`. It’s been an alias since Django 1.9. This only affects code that imports from the module directly. The `DATABASES` setting can still use `'django.db.backends.postgresql_psycopg2'`, though you can simplify that by using the `'django.db.backends.postgresql'` name added in Django 1.9.
* `django.shortcuts.render_to_response()` is deprecated in favor of `django.shortcuts.render()`. `render()` takes the same arguments except that it also requires a `request`.
* The `DEFAULT_CONTENT_TYPE` setting is deprecated. It doesn’t interact well with third-party apps and is obsolete since HTML5 has mostly superseded XHTML.
* `HttpRequest.xreadlines()` is deprecated in favor of iterating over the request.
* The `field_name` keyword argument to `QuerySet.earliest()` and `QuerySet.latest()` is deprecated in favor of passing the field names as arguments. Write `.earliest('pub_date')` instead of `.earliest(field_name='pub_date')`.
* The `weak` argument to `django.dispatch.signals.Signal.disconnect()` is removed.
* `django.db.backends.base.BaseDatabaseOperations.check_aggregate_support()` is removed.
* The `django.forms.extras` package is removed.
* The `assignment_tag` helper is removed.
* The `host` argument to `SimpleTestCase.assertsRedirects()` is removed. The compatibility layer which allows absolute URLs to be considered equal to relative ones when the path is identical is also removed.
* `Field.rel` and `Field.remote_field.to` are removed.
* The `on_delete` argument for `ForeignKey` and `OneToOneField` is now required in models and migrations. Consider squashing migrations so that you have fewer of them to update.
* `django.db.models.fields.add_lazy_relation()` is removed.
* When time zone support is enabled, database backends that don’t support time zones no longer convert aware datetimes to naive values in UTC anymore when such values are passed as parameters to SQL queries executed outside of the ORM, e.g. with `cursor.execute()`.
* d`jango.contrib.auth.tests.utils.skipIfCustomUser()` is removed.
* The `GeoManager` and `GeoQuerySet` classes are removed.
* The `django.contrib.gis.geoip` module is removed.
* The `supports_recursion` check for template loaders is removed from:
    * `django.template.engine.Engine.find_template()`
    * `django.template.loader_tags.ExtendsNode.find_template()`
    * `django.template.loaders.base.Loader.supports_recursion()`
    * `django.template.loaders.cached.Loader.supports_recursion()`
* The `load_template` and `load_template_sources` template loader methods are removed.
* The template_dirs argument for template loaders is removed:
    * `django.template.loaders.base.Loader.get_template()`
    * `django.template.loaders.cached.Loader.cache_key()`
    * `django.template.loaders.cached.Loader.get_template()`
    * `django.template.loaders.cached.Loader.get_template_sources()`
    * `django.template.loaders.filesystem.Loader.get_template_sources()`
* `django.template.loaders.base.Loader.__call__()` is removed.
* Support for custom error views that don’t accept an `exception` parameter is removed.
* The `mime_type` attribute of `django.utils.feedgenerator.Atom1Feed` and `django.utils.feedgenerator.RssFeed` is removed.
* The `app_name` argument to `include()` is removed.
* Support for passing a 3-tuple (including `admin.site.urls`) as the first argument to `include()` is removed.
* Support for setting a URL instance namespace without an application namespace is removed.
* `Field._get_val_from_obj()` is removed.
* `django.template.loaders.eggs.Loader` is removed.
* The `current_app` parameter to the `contrib.auth` function-based views is removed.
* The `callable_obj` keyword argument to `SimpleTestCase.assertRaisesMessage()` is removed.
* Support for the `allow_tags` attribute on `ModelAdmin` methods is removed.
* The `enclosure` keyword argument to `SyndicationFeed.add_item()` is removed.
* The `django.template.loader.LoaderOrigin` and `django.template.base.StringOrigin` aliases for `django.template.base.Origin` are removed.
* The `makemigrations --exit` option is removed.
* Support for direct assignment to a reverse foreign key or many-to-many relation is removed.
* The `get_srid()` and `set_srid()` methods of `django.contrib.gis.geos.GEOSGeometry` are removed.
* The `get_x()`, `set_x()`, `get_y()`, `set_y()`, `get_z()`, and `set_z()` methods of `django.contrib.gis.geos.Point` are removed.
* The `get_coords()` and `set_coords()` methods of `django.contrib.gis.geos.Point` are removed.
* The `cascaded_union` property of `django.contrib.gis.geos.MultiPolygon` is removed.
* `django.utils.functional.allow_lazy()` is removed.
* The `shell --plain` option is removed.
* The `django.core.urlresolvers` module is removed in favor of its new location, `django.urls`.
* `CommaSeparatedIntegerField` is removed, except for support in historical migrations.
* The template `Context.has_key()` method is removed.
* Support for the `django.core.files.storage.Storage.accessed_time()`, `created_time()`, and `modified_time()` methods is removed.
* Support for query lookups using the model name when `Meta.default_related_name` is set is removed.
* The MySQL `__search` lookup is removed.
* The shim for supporting custom related manager classes without a `_apply_rel_filters()` method is removed.
* Using `User.is_authenticated()` and `User.is_anonymous()` as methods rather than properties is no longer supported.
* The `Model._meta.virtual_fields` attribute is removed.
* The keyword arguments `virtual_only` in `Field.contribute_to_class()` and `virtual` in `Model._meta.add_field()` are removed.
* The `javascript_catalog()` and `json_catalog()` views are removed.
* `django.contrib.gis.utils.precision_wkt()` is removed.
* In multi-table inheritance, implicit promotion of a `OneToOneField` to a `parent_link` is removed.
* Support for `Widget._format_value()` is removed.
* `FileField` methods `get_directory_name()` and `get_filename()` are removed.
* The `mark_for_escaping()` function and the classes it uses: `EscapeData`, `EscapeBytes`, `EscapeText`, `EscapeString`, and `EscapeUnicode` are removed.
* The `escape` filter now uses `django.utils.html.conditional_escape()`.
* `Manager.use_for_related_fields` is removed.
* Model `Manager` inheritance follows MRO inheritance rules. The requirement to use `Meta.manager_inheritance_from_future` to opt-in to the behavior is removed.
* Support for old-style middleware using `settings.MIDDLEWARE_CLASSES` is removed.
#### djangorestframework (`3.6.3` to `3.11.0`)
##### 3.10.X
* Drop Python 2 support.
##### 3.9.X
* Deprecate the `Router.register` `base_name` argument in favor of `basename`
* Deprecate the `Router.get_default_base_name` method in favor of `Router.get_default_basename`
* Change `CharField` to disallow null bytes.
    * To revert to the old behavior, subclass `CharField` and remove `ProhibitNullCharactersValidator` from the validators. `python class NullableCharField(serializers.CharField): def __init__(self, *args, **kwargs): super().__init__(*args, **kwargs) self.validators = [v for v in self.validators if not isinstance(v, ProhibitNullCharactersValidator)]`
* Removed input value from `deault_error_message`
* Deprecate the `DjangoObjectPermissionsFilter` class, moved to the `djangorestframework-guardian` package.
* Drop Django 1.10 support
##### 3.8.X
* **Breaking Change:** Alter `read_only` plus `default` behaviour (`read_only` fields will now **always** be excluded from writable fields.)
* Correct `allow_null` behaviour when `required=False`
    * Without an explicit `default`, `allow_null` implies a default of `null` for outgoing serialization. Previously such fields were being skipped when read-only or otherwise not required. **Possible backwards compatibility break** if you were relying on such fields being excluded from the outgoing representation. In order to restore the old behaviour you can override `data` to exclude the field when `None`.
* Refactor dynamic route generation and improve viewset action introspectibility. `ViewSet`s have been provided with new attributes and methods that allow it to introspect its set of actions and the details of the current action.
    * Merged `list_route` and `detail_route` into a single `action` decorator.
    * Get all extra actions on a `ViewSet` with `.get_extra_actions()`.
    * Extra actions now set the `url_name` and `url_path` on the decorated method.
    * url_name is now based on the function name, instead of the url_path, as the path is not always suitable (e.g., capturing arguments in the path).
    * Enable action url reversing through `.reverse_action()` method (added in 3.7.4)
    * Example reverse call: `self.reverse_action(self.custom_action.url_name)`
    * Add `detail` init kwarg to indicate if the current action is operating on a collection or a single instance.
    * Deprecated `list_route` & `detail_route` in favor of `action` decorator with detail boolean.
    * Deprecated dynamic list/detail route variants in favor of `DynamicRoute` with `detail` boolean.
    * Refactored the router's dynamic route generation.
    * `list_route` and `detail_route` maintain the old behavior of `url_name`, basing it on the `url_path` instead of the function name.
* Remove unused `compat._resolve_model()`
* Drop compat workaround for unsupported Python 3.2
##### 3.7.X
* Drop compat wrapper for `TimeDelta.total_seconds()`
* Remove `set_rollback()` from compat
* Remove references to unsupported Django versions in docs and code
* Deprecated `exclude_from_schema` on `APIView` and `api_view decorator.Set schema=None` or `@schema(None)` as appropriate
* Removed `DjangoFilterBackend` inline with deprecation policy. Use django_filters.rest_framework.FilterSet and/or django_filters.rest_framework.DjangoFilterBackend instead.
* Remove Django 1.8 & 1.9 compatibility code
* Remove deprecated schema code from `DefaultRouter`
#### django-phonenumber-field (`2.0.0` to `4.0.0`)
##### 3.0.0
* Drop support for Django 2.0.
* Drop support for Python 2.7 and 3.4.
##### 2.3.0
* `modelfields.PhoneNumberField` now inherits from `models.CharField` instead of `models.Field`.
##### 2.1.0
* Removed hardcoded dependency to phonenumbers library. Now developers have to manually install either phonenumbers or phonenumberslite.
##### 2.0.1
* Statically depend on phonenumbers Previously the phonenumberslight dependency was used dynamically in setup.py if it already was installed, causing problems with building wheels and with pipenv.
#### celery (`4.2.0` to `4.4.5`)
##### 4.4.3
* Remove doubling of `prefetch_count` increase when `prefetch_multiplier`
##### 4.4.0rc1
* Django: Re-raise exception if ImportError not caused by missing tasks module
* Django: fixed a regression putting DB connections in invalid state when CONN_MAX_AGE != 0
##### 4.3.0 RC2
* Django: Prepend current working directory instead of appending so that the project directory will have precedence over system modules as expected.
#### django-filter (`1.1.0` to `2.3.0`)
##### 2.3.0
* Drop Django 2.1 and below
##### 2.2
* Dropped support for EOL Python 3.4
##### 2.0
* Drop python 2, Django<1.11 support
* List Django as a dependency in `setup.py`
* Replaced `super(ClassName, self)` with `super()`
* Remove `"Meta.together"` option
* removes the old/deprecated `help_text` settings. Seems they were forgotten
* Remove `Filter.name` deprecation code

