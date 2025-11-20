import { test, expect } from '@playwright/test';

test('hackathon2025 UI: initial render and REST interaction', async ({ page }) => {
  await page.goto('http://localhost:8080/');
  expect(await page.title()).toContain('Hackathon');
  const heading = page.getByRole('heading', { level: 1 });
  await expect(heading).toContainText('Hackathon 2025 Demo');
  const button = page.getByRole('button', { name: 'Test REST' });
  await expect(button).toBeVisible();
  const apiResult = page.locator('#apiResult');
  const count = await apiResult.count();
  expect(count).toBeGreaterThan(0);
  await expect(apiResult).toHaveText('');
  await button.click();
  await expect(apiResult).not.toHaveText('', { timeout: 5000 });
  const raw = await apiResult.innerText();
  const parsed: any = JSON.parse(raw);
  expect(parsed).not.toBeNull();
  expect(typeof parsed).toBe('object');
  expect(Object.keys(parsed).length).toBeGreaterThan(0);
  expect(raw.toLowerCase()).toContain('hello');
});

test('API: GET /api/hello returns JSON with hello message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello');
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  const msg = String(json.message || '');
  expect(msg.toLowerCase()).toContain('hello');
});

test('API: GET /api/hello2 returns JSON with dummy text', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello2');
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  const msg = String(json.message || '');
  expect(msg.toLowerCase()).toContain('dummy');
});

test('API: GET /api/hello3 returns JSON with dummy text', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello3');
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  const msg = String(json.message || '');
  expect(msg.toLowerCase()).toContain('dummy');
});

test('API: GET /api/hello2alt returns JSON with hello-like message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello2alt');
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  const msg = String(json.message || '');
  expect(msg.toLowerCase()).toContain('hello');
});

test('API: GET /api/goodby with name param returns personalized goodbye message', async ({ request }) => {
  const name = 'Alice';
  const res = await request.get(`http://localhost:8080/api/goodby?name=${encodeURIComponent(name)}`);
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  const msg = String(json.message || '').toLowerCase();
  expect(msg).toContain('goodbye');
  expect(msg).toContain(name.toLowerCase());
});

test('API: GET /api/goodnight returns JSON with good night message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/goodnight');
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  const msg = String(json.message || '').toLowerCase();
  expect(msg).toMatch(/good\s+night/);
});

test('API: GET /api/nature-image returns keyword and imageUrl for known keyword', async ({ request }) => {
  const keyword = 'tree';
  const res = await request.get(`http://localhost:8080/api/nature-image?keyword=${encodeURIComponent(keyword)}`);
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  expect(String(json.keyword || '').toLowerCase()).toContain(keyword);
  expect(typeof json.imageUrl).toBe('string');
  expect(String(json.imageUrl)).toMatch(/^https?:\/\//);
});

test('API: GET /api/fibonacci returns fibonacci number for given input', async ({ request }) => {
  const number = 10;
  const res = await request.get(`http://localhost:8080/api/fibonacci?number=${number}`);
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  expect(Number(json.number)).toBe(number);
  expect(typeof json.fibonacci).toBe('number');
  expect(Number(json.fibonacci)).toBe(55);
});

test('hackathon2025 UI: render followup page', async ({ page }) => {
  await page.goto('http://localhost:8080/followup');
  const heading = page.getByRole('heading', { level: 1 });
  await expect(heading).toBeVisible();
});