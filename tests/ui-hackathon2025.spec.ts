import { test, expect } from '@playwright/test';

test('index page shows title, heading, Test REST button and API result updates after click', async ({ page }) => {
  await page.goto('http://localhost:8080/');

  await expect(page).toHaveTitle(/Hackathon/);

  const heading = page.getByRole('heading', { level: 1, name: /Hackathon 2025 Demo/ });
  await expect(heading).toHaveText(/Hackathon 2025 Demo/);

  const button = page.getByRole('button', { name: 'Test REST' });
  await expect(button).toBeVisible();

  const api = page.locator('#apiResult');
  await expect(api).toBeAttached();
  await expect(api).toHaveText('');

  await button.click();

  await expect(api).not.toHaveText('');

  const raw = (await api.textContent()) ?? '';
  const text = raw.trim();
  expect(text.length).toBeGreaterThan(0);
  expect(() => JSON.parse(text)).not.toThrow();
  const parsed = JSON.parse(text);
  expect(parsed && typeof parsed === 'object').toBeTruthy();
  expect(Object.keys(parsed).length).toBeGreaterThan(0);
  expect(text.toLowerCase()).toContain('hello');
});