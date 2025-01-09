import { test, expect } from '@playwright/test';

test('example test', async ({ page }) => {
    await page.goto('https://example.com');
    await page.click('text=More information...');
    await expect(page).toHaveURL(/.*more-info/);
});