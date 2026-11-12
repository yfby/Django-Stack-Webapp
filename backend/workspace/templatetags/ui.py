from django import template
from django.utils.safestring import mark_safe
register = template.Library()
PATHS = {
 "grid": '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
 "inbox": '<path d="M4 4h16l2 12v4H2v-4L4 4Z"/><path d="M2 14h6l2 3h4l2-3h6"/>',
 "queue": '<path d="M4 6h16M4 12h10M4 18h6m6-3 4 3-4 3"/>',
 "workflow": '<rect x="3" y="3" width="6" height="6" rx="1"/><rect x="15" y="15" width="6" height="6" rx="1"/><path d="M6 9v9h9m-3-3 3 3-3 3M9 6h9v6"/>',
 "chart": '<path d="M4 3v17h17M9 15V9m5 6V5m5 10v-4"/>',
 "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 "archive": '<rect x="3" y="3" width="18" height="4" rx="1"/><path d="M5 7v14h14V7m-10 5h6"/>',
 "team": '<circle cx="9" cy="8" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3m1-16a3 3 0 0 1 0 6m2 4a5 5 0 0 1 3 4v2"/>',
 "settings": '<path d="M4 7h16M4 17h16"/><circle cx="9" cy="7" r="3"/><circle cx="15" cy="17" r="3"/>',
 "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
 "plus": '<path d="M12 5v14M5 12h14"/>',
 "arrow": '<path d="M4 12h16m-6-6 6 6-6 6"/>',
 "check": '<path d="m5 12 4 4L19 6"/>',
 "chevron": '<path d="m8 10 4 4 4-4"/>',
 "download": '<path d="M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4"/>',
 "book": '<path d="M12 5v16M3 3l9 2 9-2v16l-9 2-9-2V3Z"/>',
 "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
 "logout": '<path d="M9 4H3v16h6m5-14 6 6-6 6M8 12h12"/>',
 "bolt": '<path d="m13 2-9 12h7l-1 8 10-12h-7l1-8Z"/>',
 "printer": '<path d="M6 9V3h12v6M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="7" rx="1"/><path d="M18 12h.01"/>',
 "paper": '<path d="M6 2h8l4 4v16H6z"/><path d="M14 2v5h5M9 12h6m-6 4h6"/>',
 "cut": '<circle cx="6" cy="6" r="2.5"/><circle cx="6" cy="18" r="2.5"/><path d="M8 8l11 11M8 16 19 5"/>',
 "spark": '<path d="M12 2v4m0 12v4M2 12h4m12 0h4M4.9 4.9l2.8 2.8m8.6 8.6 2.8 2.8M19.1 4.9l-2.8 2.8M7.7 16.3l-2.8 2.8"/><circle cx="12" cy="12" r="3"/>',
 "flag": '<path d="M5 22V3m0 1c5-5 9 5 14 0v11c-5 5-9-5-14 0"/>',
 "note": '<path d="M4 3h16v18H4zM8 8h8m-8 4h8m-8 4h4"/>',
}
@register.simple_tag
def icon(name):
    path = PATHS.get(name, PATHS["grid"])
    return mark_safe('<svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+path+'</svg>')
