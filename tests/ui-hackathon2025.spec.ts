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

test('GET /api/hello returns JSON with a hello message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello');
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeTruthy();
  expect(typeof body).toBe('object');
  expect(Object.keys(body).length).toBeGreaterThan(0);
  const msg = String(body.message ?? '');
  expect(msg.toLowerCase()).toContain('hello');
});

test('GET /api/hello2 returns JSON with a message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello2');
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeTruthy();
  expect(typeof body).toBe('object');
  expect(Object.keys(body).length).toBeGreaterThan(0);
  const msg = String(body.message ?? '');
  expect(msg.length).toBeGreaterThan(0);
  // message is a dummy hello-like text; check it contains 'dummy' or is non-empty
  expect(/dummy|hello/i.test(msg) || msg.length > 0).toBeTruthy();
});

test('GET /api/hello3 returns JSON with a message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello3');
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeTruthy();
  expect(typeof body).toBe('object');
  expect(Object.keys(body).length).toBeGreaterThan(0);
  const msg = String(body.message ?? '');
  expect(msg.length).toBeGreaterThan(0);
});

test('GET /api/goodby returns JSON with a goodbye message (uses default name)', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/goodby');
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeTruthy();
  expect(typeof body).toBe('object');
  expect(Object.keys(body).length).toBeGreaterThan(0);
  const msg = String(body.message ?? '');
  expect(msg.toLowerCase()).toContain('goodbye');
});

test('GET /api/goodnight returns JSON with a good night message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/goodnight');
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeTruthy();
  expect(typeof body).toBe('object');
  expect(Object.keys(body).length).toBeGreaterThan(0);
  const msg = String(body.message ?? '');
  expect(/good\s+night/i.test(msg)).toBeTruthy();
});

test('hackathon2025 UI: render followup page', async ({ page }) => {
  await page.goto('http://localhost:8080/followup');
  const heading = page.getByRole('heading', { level: 1 });
  await expect(heading).toBeVisible();
});