import { test, expect } from '@playwright/test';

test('hackathon2025 UI: initial render and REST interaction', async ({ page }) => {
  await page.goto('http://localhost:8080/');

  await expect(page).toHaveTitle(/Hackathon/);

  const h1 = page.getByRole('heading', { level: 1 });
  await expect(h1).toHaveText(/Hackathon 2025 Demo/);

  const testRestButton = page.getByRole('button', { name: 'Test REST' });
  await expect(testRestButton).toBeVisible();

  const apiResult = page.locator('#apiResult');
  const count = await apiResult.count();
  expect(count).toBeGreaterThan(0);

  await expect(apiResult).toHaveText('');

  await testRestButton.click();

  await expect(apiResult).not.toHaveText('', { timeout: 5000 });

  const text = await apiResult.innerText();
  let parsed: any = null;
  try {
    parsed = JSON.parse(text);
  } catch (e) {
    parsed = null;
  }
  expect(parsed).not.toBeNull();
  expect(typeof parsed).toBe('object');
  expect(Object.keys(parsed).length).toBeGreaterThan(0);
  expect(text.toLowerCase()).toContain('hello');
});