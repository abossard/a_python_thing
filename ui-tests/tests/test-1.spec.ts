import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://microsoftedge.github.io/Demos/demo-to-do/');
  await page.getByPlaceholder('Try typing \'Buy milk\'').click();
  await page.getByPlaceholder('Try typing \'Buy milk\'').fill('Hello');
  await page.getByPlaceholder('Try typing \'Buy milk\'').press('Enter');
  await page.getByRole('button', { name: '➡️' }).click();
  await page.getByLabel('Hello').check();
  
});