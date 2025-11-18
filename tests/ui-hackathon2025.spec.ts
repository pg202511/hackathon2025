import { test, expect } from '@playwright/test';

test('hackathon2025 UI: initial render and REST interaction', async ({ page }) => {
  await page.goto('http://localhost:8080/');

  await expect(page).toHaveTitle(/Hackathon/);

  const heading = page.getByRole('heading', { level: 1 });
  await expect(heading).toHaveText('Hackathon 2025 Demo');

  const button = page.getByRole('button', { name: 'Test REST' });
  await expect(button).toBeVisible();

  const apiResult = page.locator('#apiResult');
  const count = await apiResult.count();
  expect(count).toBeGreaterThan(0);
  await expect(apiResult).toHaveText('');

  await button.click();

  await expect(apiResult).not.toHaveText('', { timeout: 5000 });

  const raw = await apiResult.innerText();
  const parsed = JSON.parse(raw);
  expect(parsed).not.toBeNull();
  expect(typeof parsed).toBe('object');
  expect(Object.keys(parsed).length).toBeGreaterThan(0);
  expect(raw.toLowerCase()).toContain('hello');
});