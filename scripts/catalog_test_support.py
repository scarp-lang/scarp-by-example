"""Independent expected catalog inventory shared by the offline site tests.

Update this reviewed count when deliberately adding/removing routes. Do not
derive it from build_site output: that would hide accidental route loss.
Individual tests still check their own routes, source fidelity and links.
"""

# 91 prior catalog pages + numerical workshop index + three lesson pages.
EXPECTED_PAGE_COUNT = 95
