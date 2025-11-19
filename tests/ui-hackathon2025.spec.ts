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
  const body: any = await res.json();
  expect(body).toBeTruthy();
  expect(typeof body).toBe('object');
  expect(Object.keys(body).length).toBeGreaterThan(0);
  const msg = String(body.message || '');
  expect(msg.toLowerCase()).toContain('hello');
});

test('API: GET /api/hello2 returns JSON containing hello/dummy text', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello2');
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeTruthy();
  expect(typeof body).toBe('object');
  expect(Object.keys(body).length).toBeGreaterThan(0);
  const msg = String(body.message || '');
  expect(msg.toLowerCase()).toContain('hello');
});

test('API: GET /api/hello3 returns JSON containing hello/dummy text', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello3');
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeTruthy();
  expect(typeof body).toBe('object');
  expect(Object.keys(body).length).toBeGreaterThan(0);
  const msg = String(body.message || '');
  expect(msg.toLowerCase()).toContain('hello');
});

test('API: GET /api/goodby returns JSON with goodbye message including provided name', async ({ request }) => {
  const name = 'Alice';
  const res = await request.get(`http://localhost:8080/api/goodby?name=${encodeURIComponent(name)}`);
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeTruthy();
  expect(typeof body).toBe('object');
  expect(Object.keys(body).length).toBeGreaterThan(0);
  const msg = String(body.message || '');
  expect(msg.toLowerCase()).toContain('goodbye');
  expect(msg.toLowerCase()).toContain(name.toLowerCase());
});

test('API: GET /api/goodnight returns JSON with good night message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/goodnight');
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeTruthy();
  expect(typeof body).toBe('object');
  expect(Object.keys(body).length).toBeGreaterThan(0);
  const msg = String(body.message || '').toLowerCase();
  expect(msg).toMatch(/good\s+night/);
});

test('hackathon2025 UI: render followup page', async ({ page }) => {
  await page.goto('http://localhost:8080/followup');
  const heading = page.getByRole('heading', { level: 1 });
  await expect(heading).toBeVisible();
});