# Django Admin — Complete Setup Guide (One by One)

> Based on the official Django 6.0 documentation: https://docs.djangoproject.com/en/6.0/ref/contrib/admin/

---

## 🟢 #1 — Simplest Setup: Just Register a Model

No customization. Django auto-generates everything.

```python
# admin.py
from django.contrib import admin
from myapp.models import Author

admin.site.register(Author)
```

✅ Shows all editable fields automatically. Good starting point.

---

## 🟡 #2 — Using a `ModelAdmin` Class

When you want to customize admin behavior, create a `ModelAdmin` class:

```python
from django.contrib import admin
from myapp.models import Author

class AuthorAdmin(admin.ModelAdmin):
    pass  # ready for customization

admin.site.register(Author, AuthorAdmin)
```

---

## 🟡 #3 — Using the `@admin.register` Decorator

Cleaner, modern way. No need for `admin.site.register()` at the bottom:

```python
from django.contrib import admin
from myapp.models import Author

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass
```

Register multiple models at once:

```python
@admin.register(Author, Editor, Reader)
class PersonAdmin(admin.ModelAdmin):
    pass
```

---

## 🟠 #4 — Controlling Which Fields to Show: `fields` and `exclude`

### Using `fields` — show only specific fields (in order):
```python
class AuthorAdmin(admin.ModelAdmin):
    fields = ["name", "title"]
```

### Put two fields on the same row by wrapping in a tuple:
```python
class FlatPageAdmin(admin.ModelAdmin):
    fields = [("url", "title"), "content"]
```

### Using `exclude` — show everything EXCEPT these:
```python
class AuthorAdmin(admin.ModelAdmin):
    exclude = ["birth_date"]
```

> 💡 `fields` and `exclude` do the opposite of each other. Use whichever is shorter.

---

## 🟠 #5 — Grouping Fields into Sections: `fieldsets`

`fieldsets` lets you group fields into named sections on the form:

```python
class FlatPageAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,  # Section with no title
            {
                "fields": ["url", "title", "content", "sites"],
            },
        ),
        (
            "Advanced Options",  # Section title
            {
                "classes": ["collapse"],  # Collapsed by default
                "fields": ["registration_required", "template_name"],
            },
        ),
    ]
```

### `field_options` keys inside each section:

| Key | Purpose |
|---|---|
| `fields` | List of fields to show in this section (required) |
| `classes` | CSS classes — use `"collapse"` to make it collapsible, `"wide"` for extra space |
| `description` | Text shown at the top of the section |

---

## 🟠 #6 — Controlling the List View: `list_display`

Controls which columns appear in the change list (the main table of records):

```python
class PersonAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "birthday"]
```

### You can also show:
- A related field using `__` notation: `"city__name"`
- A custom method:

```python
class PersonAdmin(admin.ModelAdmin):
    list_display = ["first_name", "upper_case_name"]

    @admin.display(description="Name")
    def upper_case_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".upper()
```

- A boolean icon (✅/❌):

```python
@admin.display(boolean=True)
def born_in_fifties(self):
    return 1950 <= self.birthday.year < 1960
```

- Custom HTML using `format_html`:

```python
from django.utils.html import format_html

@admin.display
def colored_name(self):
    return format_html('<span style="color: #{};">{} {}</span>',
        self.color_code, self.first_name, self.last_name)
```

---

## 🟠 #7 — Making List Columns Clickable: `list_display_links`

By default, only the first column links to the edit page. You can change that:

```python
class PersonAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "birthday"]
    list_display_links = ["first_name", "last_name"]  # both are links
```

Disable all links (no row is clickable):
```python
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "message"]
    list_display_links = None
```

---

## 🟠 #8 — Editing Directly from the List View: `list_editable`

Makes fields editable directly in the list (no need to open each record):

```python
class PersonAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "age"]
    list_editable = ["age"]
```

> ⚠️ Rules:
> - The field must also be in `list_display`
> - It cannot also be in `list_display_links`

---

## 🟠 #9 — Adding Filters Sidebar: `list_filter`

Adds a filter panel on the right side of the list:

```python
class PersonAdmin(admin.ModelAdmin):
    list_filter = ["country", "is_active", "birthday"]
```

---

## 🟠 #10 — Adding a Search Box: `search_fields`

```python
class PersonAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name", "email"]
```

### Search across related models with `__`:
```python
search_fields = ["user__email"]
```

### Search type prefixes:
| Prefix | Lookup type |
|---|---|
| `^` | Starts with (`istartswith`) |
| `=` | Exact match (`iexact`) |
| `@` | Full-text search (`search`) |
| *(none)* | Contains (`icontains`) — default |

```python
search_fields = ["^first_name", "=email"]  # starts-with + exact
```

Add helper text below the search box:
```python
class PersonAdmin(admin.ModelAdmin):
    search_help_text = "Search by name or email"
```

---

## 🟠 #11 — Date Drill-Down Navigation: `date_hierarchy`

Adds a date-based navigation bar (Year → Month → Day):

```python
class ArticleAdmin(admin.ModelAdmin):
    date_hierarchy = "pub_date"
```

Works with related models too:
```python
date_hierarchy = "author__pub_date"
```

---

## 🟠 #12 — Default Ordering in List View: `ordering`

```python
class PersonAdmin(admin.ModelAdmin):
    ordering = ["last_name", "first_name"]   # A-Z
    # ordering = ["-created_at"]             # Newest first
```

---

## 🟠 #13 — Pagination: `list_per_page` and `list_max_show_all`

```python
class PersonAdmin(admin.ModelAdmin):
    list_per_page = 50       # Show 50 per page (default: 100)
    list_max_show_all = 500  # "Show all" appears only if ≤ 500 records
```

---

## 🟠 #14 — Read-Only Fields: `readonly_fields`

Displays fields as plain text (not editable):

```python
class PersonAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at", "updated_at"]
```

You can also show computed/method output as read-only:

```python
class PersonAdmin(admin.ModelAdmin):
    readonly_fields = ["address_report"]

    @admin.display(description="Full Address")
    def address_report(self, instance):
        return ", ".join(instance.get_full_address())
```

---

## 🟠 #15 — Auto-Fill Slug Fields: `prepopulated_fields`

Automatically fills a `slug` field from another field using JavaScript:

```python
class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["title"]}
```

> ✅ As you type the title, the slug fills in automatically. Once saved, it stops changing.

---

## 🟠 #16 — ManyToMany Widget Options: `filter_horizontal` / `filter_vertical`

By default, ManyToMany fields use a boring `<select multiple>`.
These options replace it with a searchable two-panel widget:

```python
class ArticleAdmin(admin.ModelAdmin):
    filter_horizontal = ["tags"]   # Side by side panels
    # filter_vertical = ["tags"]   # Top/bottom panels
```

---

## 🟠 #17 — ForeignKey as Radio Buttons: `radio_fields`

Instead of a dropdown, show radio buttons for ForeignKey or choices fields:

```python
class PersonAdmin(admin.ModelAdmin):
    radio_fields = {"group": admin.VERTICAL}
    # or: radio_fields = {"group": admin.HORIZONTAL}
```

---

## 🟠 #18 — Autocomplete for ForeignKey: `autocomplete_fields`

Replaces the dropdown with a searchable Select2 autocomplete input.
Great for large related datasets:

```python
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ["question_text"]  # Required on the related model!

class ChoiceAdmin(admin.ModelAdmin):
    autocomplete_fields = ["question"]
```

> ⚠️ The related model's `ModelAdmin` **must** define `search_fields`.

---

## 🟠 #19 — ForeignKey as Raw ID Input: `raw_id_fields`

Instead of loading all related objects into a dropdown (slow!), show a plain input with a lookup magnifier button:

```python
class ArticleAdmin(admin.ModelAdmin):
    raw_id_fields = ["newspaper"]
```

> ✅ Best for ForeignKey to large tables.

---

## 🟠 #20 — Custom Form: `form`

Replace the auto-generated form with your own `ModelForm`:

```python
from django import forms

class AuthorForm(forms.ModelForm):
    extra_notes = forms.CharField()  # Add a custom field

    class Meta:
        model = Author
        fields = "__all__"

class AuthorAdmin(admin.ModelAdmin):
    form = AuthorForm
```

---

## 🟠 #21 — Override Widget for a Field Type: `formfield_overrides`

Change the widget for a specific field type across all fields of that type:

```python
from django.contrib import admin
from django.db import models
from myapp.widgets import RichTextEditorWidget

class MyModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {"widget": RichTextEditorWidget},
    }
```

---

## 🟠 #22 — Save Buttons: `save_on_top`, `save_as`, `save_as_continue`

```python
class ArticleAdmin(admin.ModelAdmin):
    save_on_top = True        # Show save buttons at TOP of form too
    save_as = True            # Replace "Save and add another" with "Save as new"
    save_as_continue = False  # After "Save as new", go to list (not edit page)
```

---

## 🟠 #23 — Empty Value Display: `empty_value_display`

What to show when a field is `None` or blank (default is `-`):

```python
class AuthorAdmin(admin.ModelAdmin):
    empty_value_display = "N/A"
```

Per-field override:
```python
@admin.display(empty_value="Unknown")
def view_birth_date(self, obj):
    return obj.birth_date
```

---

## 🟠 #24 — "View on Site" Link: `view_on_site`

```python
class PersonAdmin(admin.ModelAdmin):
    view_on_site = False  # Hide the "View on site" button
```

Or use a custom URL:
```python
class PersonAdmin(admin.ModelAdmin):
    def view_on_site(self, obj):
        return f"https://example.com/people/{obj.slug}/"
```

---

## 🔴 #25 — Inline Models: `inlines` (StackedInline / TabularInline)

Show related models **inside** the parent model's edit page.

### TabularInline — compact table layout:
```python
class BookInline(admin.TabularInline):
    model = Book
    extra = 1  # how many blank rows to show

class AuthorAdmin(admin.ModelAdmin):
    inlines = [BookInline]
```

### StackedInline — full form layout (one per block):
```python
class BookInline(admin.StackedInline):
    model = Book
    extra = 1
```

---

## 🔴 #26 — Custom Admin Actions: `actions`

Add bulk actions to the list view (besides the default "Delete"):

```python
@admin.action(description="Mark selected as published")
def make_published(modeladmin, request, queryset):
    queryset.update(status="published")

class ArticleAdmin(admin.ModelAdmin):
    actions = [make_published]
    actions_on_top = True     # Show action bar at top (default)
    actions_on_bottom = False # Optionally also at bottom
```

---

## 🔴 #27 — Override Save Behavior: `save_model`

Hook into saving to add extra logic (e.g. attach the current user):

```python
class ArticleAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.author = request.user  # auto-assign author
        super().save_model(request, obj, form, change)
```

---

## 🔴 #28 — Override Delete Behavior: `delete_model`

```python
class ArticleAdmin(admin.ModelAdmin):
    def delete_model(self, request, obj):
        # Do something before deleting
        obj.notify_author()
        super().delete_model(request, obj)
```

---

## 🔴 #29 — Permission Control

Override who can do what:

```python
class ArticleAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return request.user.is_superuser  # only superusers can add

    def has_change_permission(self, request, obj=None):
        return True  # everyone can edit

    def has_delete_permission(self, request, obj=None):
        return False  # nobody can delete from admin

    def has_view_permission(self, request, obj=None):
        return True
```

---

## 🔴 #30 — Filter Queryset by Current User: `get_queryset`

Only show the logged-in user's own objects:

```python
class ArticleAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
```

---

## 🔴 #31 — Dynamic Ordering per User: `get_ordering`

```python
class PersonAdmin(admin.ModelAdmin):
    def get_ordering(self, request):
        if request.user.is_superuser:
            return ["name", "rank"]
        return ["name"]
```

---

## 🔴 #32 — Custom Search Logic: `get_search_results`

Add your own search logic (e.g. search by integer field):

```python
class PersonAdmin(admin.ModelAdmin):
    search_fields = ["name"]

    def get_search_results(self, request, queryset, search_term):
        queryset, dupes = super().get_search_results(request, queryset, search_term)
        try:
            queryset |= self.model.objects.filter(age=int(search_term))
        except ValueError:
            pass
        return queryset, dupes
```

---

## 🔴 #33 — Filter ForeignKey Choices: `formfield_for_foreignkey`

Limit which related objects appear in a ForeignKey dropdown:

```python
class MyModelAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "car":
            kwargs["queryset"] = Car.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
```

Same for ManyToMany:
```python
def formfield_for_manytomany(self, db_field, request, **kwargs):
    if db_field.name == "cars":
        kwargs["queryset"] = Car.objects.filter(owner=request.user)
    return super().formfield_for_manytomany(db_field, request, **kwargs)
```

---

## 🔴 #34 — Add Custom URL Views: `get_urls`

Add your own pages inside the admin:

```python
from django.urls import path
from django.template.response import TemplateResponse

class MyModelAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("my_view/", self.admin_site.admin_view(self.my_view))
        ]
        return my_urls + urls  # custom URLs FIRST

    def my_view(self, request):
        context = dict(
            self.admin_site.each_context(request),
            my_data="hello"
        )
        return TemplateResponse(request, "admin/my_template.html", context)
```

---

## 🔴 #35 — Custom Admin Site: `AdminSite`

Create a completely separate admin interface (e.g. for different user groups):

```python
# admin_site.py
from django.contrib.admin import AdminSite

class MyAdminSite(AdminSite):
    site_header = "My Company Admin"
    site_title = "My Admin Portal"
    index_title = "Welcome"

my_admin_site = MyAdminSite(name="myadmin")
```

```python
# urls.py
from myapp.admin_site import my_admin_site

urlpatterns = [
    path("my-admin/", my_admin_site.urls),
]
```

Register models to the custom site:
```python
@admin.register(Author, site=my_admin_site)
class AuthorAdmin(admin.ModelAdmin):
    pass
```

---

## 🔴 #36 — Custom Admin Templates

Override the default HTML templates for any admin view:

```python
class ArticleAdmin(admin.ModelAdmin):
    change_form_template = "admin/myapp/article/change_form.html"
    change_list_template = "admin/myapp/article/change_list.html"
    add_form_template    = "admin/myapp/article/add_form.html"
    delete_confirmation_template = "admin/myapp/article/delete_confirmation.html"
    object_history_template = "admin/myapp/article/object_history.html"
```

In the template, extend the base admin layout:
```html
{% extends "admin/base_site.html" %}
{% block content %}
  <h1>My Custom Form</h1>
{% endblock %}
```

---

## 📋 Quick Reference Cheat Sheet

| Option | What it does |
|---|---|
| `list_display` | Columns shown in the list view |
| `list_display_links` | Which columns are clickable links |
| `list_editable` | Fields editable directly in the list |
| `list_filter` | Right-sidebar filter panel |
| `search_fields` | Enables search box |
| `date_hierarchy` | Date drill-down nav bar |
| `ordering` | Default sort order |
| `list_per_page` | Rows per page (default 100) |
| `fields` | Which fields to show on form |
| `exclude` | Which fields to hide from form |
| `fieldsets` | Group fields into named sections |
| `readonly_fields` | Fields shown but not editable |
| `prepopulated_fields` | Auto-fill (e.g. slug from title) |
| `filter_horizontal` | Better ManyToMany widget |
| `radio_fields` | ForeignKey as radio buttons |
| `autocomplete_fields` | ForeignKey as searchable Select2 |
| `raw_id_fields` | ForeignKey as raw ID input |
| `inlines` | Show related models inline |
| `actions` | Bulk actions in list view |
| `save_on_top` | Save buttons at top of form |
| `save_as` | "Save as new" button |
| `empty_value_display` | What to show for empty values |
| `view_on_site` | Toggle/customize "View on site" link |
| `form` | Custom ModelForm |
| `formfield_overrides` | Override widget for field type |
