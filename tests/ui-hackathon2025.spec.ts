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

test('API GET /api/hello should return JSON with hello message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello');
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(json).not.toBeNull();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  const msg = String(json.message || '');
  expect(msg.toLowerCase()).toContain('hello');
});

test('API GET /api/hello2alt should return JSON with hello2 message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello2alt');
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(json).not.toBeNull();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  const msg = String(json.message || '');
  expect(msg.toLowerCase()).toContain('hello');
});

test('API GET /api/hello2 should return JSON with message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello2');
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(json).not.toBeNull();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  const msg = String(json.message || '');
  expect(msg.length).toBeGreaterThan(0);
});

test('API GET /api/hello3 should return JSON with message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello3');
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(json).not.toBeNull();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  const msg = String(json.message || '');
  expect(msg.length).toBeGreaterThan(0);
});

test('API GET /api/goodby should return JSON with goodbye message containing name', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/goodby?name=Alice');
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(json).not.toBeNull();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  const msg = String(json.message || '').toLowerCase();
  expect(msg).toContain('goodbye');
  expect(msg).toContain('alice');
});

test('API GET /api/goodnight should return JSON with good night message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/goodnight');
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(json).not.toBeNull();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  const msg = String(json.message || '');
  expect(msg.toLowerCase()).toMatch(/good\s+night/);
});

test('API GET /api/nature-image should return JSON with keyword and imageUrl', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/nature-image?keyword=river');
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(json).not.toBeNull();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  expect(String(json.keyword || '').toLowerCase()).toBe('river');
  const imageUrl = String(json.imageUrl || '');
  expect(imageUrl.length).toBeGreaterThan(0);
  expect(imageUrl).toMatch(/^https?:\/\//);
});

test('API GET /api/fibonacci should return JSON with number and fibonacci value', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/fibonacci?number=10');
  expect(res.status()).toBe(200);
  const json: any = await res.json();
  expect(json).not.toBeNull();
  expect(typeof json).toBe('object');
  expect(Object.keys(json).length).toBeGreaterThan(0);
  expect(Number(json.number)).toBe(10);
  expect(Number(json.fibonacci)).toBe(55);
});

test('hackathon2025 UI: render followup page', async ({ page }) => {
  await page.goto('http://localhost:8080/followup');
  const heading = page.getByRole('heading', { level: 1 });
  await expect(heading).toBeVisible();
});