from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).parent / 'docs'
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.articles=[]; self.images=[]; self.ids=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='a': self.links.append(a.get('href',''))
        if tag=='article': self.articles.append(a.get('id'))
        if tag=='img': self.images.append(a)
        if 'id' in a: self.ids.append(a['id'])

class PortfolioTests(unittest.TestCase):
    def test_image_led_theme_is_dark_and_neutral_on_both_pages(self):
        css = (ROOT / 'styles.css').read_text()
        self.assertIn('color-scheme: dark;', css)
        self.assertIn('--ground: #101114;', css)
        self.assertIn('radial-gradient', css)
        for name in ['dinnerplate', 'flowdesk-live', 'sat-focus-mode', 'cachebuddy']:
            self.assertIn(name + '-ambient.webp', css)
            self.assertTrue((ROOT / (name + '-ambient.webp')).exists())
        self.assertNotIn('#64ff91', css)
        self.assertIn('ui-monospace', css)
        for name in ['index.html', 'site-notice.html']:
            html = (ROOT / name).read_text()
            self.assertIn('name="theme-color" content="#101114"', html)
        self.assertNotIn('Built to be used.', (ROOT / 'index.html').read_text())

    def test_all_four_projects_have_live_and_available_source_links(self):
        p=Page(); p.feed((ROOT/'index.html').read_text())
        self.assertEqual(set(p.articles), {'dinnerplate','flowdesk','sat-study-room','cachebuddy'})
        for url in ['https://dinnerplate.party/','https://flowdesk.party/',
                    'https://yapperyap.github.io/sat-study-room/',
                    'https://yapperyap.github.io/CacheBuddyExtension/',
                    'https://github.com/yapperyap/dinnerplate-party',
                    'https://github.com/yapperyap/sat-study-room',
                    'https://github.com/yapperyap/CacheBuddyExtension']:
            self.assertIn(url,p.links)
        for href in p.links:
            if href.startswith('#'): self.assertIn(href[1:],p.ids)
        self.assertEqual(len(p.ids),len(set(p.ids)))
        for img in p.images:
            self.assertIn('alt',img); self.assertIn('width',img); self.assertIn('height',img)
            self.assertTrue((ROOT/img['src']).exists())
        self.assertNotIn('builds<br>for the web', (ROOT/'index.html').read_text())

if __name__=='__main__': unittest.main()
