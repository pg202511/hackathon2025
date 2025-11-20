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

test('api: GET /api/hello returns hello message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello');
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeInstanceOf(Object);
  expect(Object.keys(body).length).toBeGreaterThan(0);
  expect(String(body.message).toLowerCase()).toContain('hello');
});

test('api: GET /api/hello2alt returns hello2 message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello2alt');
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeInstanceOf(Object);
  expect(Object.keys(body).length).toBeGreaterThan(0);
  expect(String(body.message).toLowerCase()).toContain('hello');
});

test('api: GET /api/hello2 returns dummy message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello2');
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeInstanceOf(Object);
  expect(Object.keys(body).length).toBeGreaterThan(0);
  expect(String(body.message).toLowerCase()).toContain('dummy');
});

test('api: GET /api/hello3 returns dummy message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/hello3');
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeInstanceOf(Object);
  expect(Object.keys(body).length).toBeGreaterThan(0);
  expect(String(body.message).toLowerCase()).toContain('dummy');
});

test('api: GET /api/goodby without name uses default and contains goodbye', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/goodby');
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeInstanceOf(Object);
  expect(Object.keys(body).length).toBeGreaterThan(0);
  expect(String(body.message).toLowerCase()).toContain('goodbye');
  expect(String(body.message).toLowerCase()).toMatch(/gast|guest|gast/);
});

test('api: GET /api/goodby with name parameter includes the name', async ({ request }) => {
  const name = 'Alice';
  const res = await request.get(`http://localhost:8080/api/goodby?name=${encodeURIComponent(name)}`);
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeInstanceOf(Object);
  expect(Object.keys(body).length).toBeGreaterThan(0);
  expect(String(body.message).toLowerCase()).toContain('goodbye');
  expect(String(body.message).toLowerCase()).toContain(name.toLowerCase());
});

test('api: GET /api/goodnight returns good night message', async ({ request }) => {
  const res = await request.get('http://localhost:8080/api/goodnight');
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeInstanceOf(Object);
  expect(Object.keys(body).length).toBeGreaterThan(0);
  expect(String(body.message).toLowerCase()).toMatch(/good\s+night/);
});

test('api: GET /api/nature-image with keyword returns keyword and imageUrl', async ({ request }) => {
  const keyword = 'river';
  const res = await request.get(`http://localhost:8080/api/nature-image?keyword=${encodeURIComponent(keyword)}`);
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeInstanceOf(Object);
  expect(Object.keys(body).length).toBeGreaterThan(0);
  expect(String(body.keyword)).toBe(keyword);
  expect(typeof body.imageUrl).toBe('string');
  expect(body.imageUrl.length).toBeGreaterThan(0);
  expect(String(body.imageUrl).toLowerCase()).toContain('http');
});

test('api: GET /api/fibonacci with number returns fibonacci calculation', async ({ request }) => {
  const number = 10;
  const res = await request.get(`http://localhost:8080/api/fibonacci?number=${number}`);
  expect(res.status()).toBe(200);
  const body: any = await res.json();
  expect(body).toBeInstanceOf(Object);
  expect(Object.keys(body).length).toBeGreaterThan(0);
  expect(Number(body.number)).toBe(number);
  expect(Number(body.fibonacci)).toBe(55);
});

test('hackathon2025 UI: render followup page', async ({ page }) => {
  await page.goto('http://localhost:8080/followup');
  const heading = page.getByRole('heading', { level: 1 });
  await expect(heading).toBeVisible();
});