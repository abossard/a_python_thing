import { test, expect } from '@playwright/test';


/*

Example HTML:
<form>
      <div class="new-task-form" tabindex="0">
        <label for="new-task">➕ Add a task</label>
        <input id="new-task" autocomplete="off" type="text" placeholder="Try typing 'Buy milk'" title="Click to start adding a task">
        <input type="submit" value="➡️">
      </div>
      <ul id="tasks"><li class="divider">To do</li>
      <li class="task">
        <label title="Complete task">
          <input type="checkbox" value="sdvgyej7r" class="box" title="Complete task">
          <span class="text">Walk the dog</span>
        </label>
        <button type="button" data-task="sdvgyej7r" class="delete" title="Delete task">╳</button>
      </li>
      <li class="task">
        <label title="Complete task">
          <input type="checkbox" value="wqqux50e1" class="box" title="Complete task">
          <span class="text">Buy groceries</span>
        </label>
        <button type="button" data-task="wqqux50e1" class="delete" title="Delete task">╳</button>
      </li></ul>
    </form> 

    */
test('test', async ({ page }) => {
  // KEEP THIS URL
  await page.goto('https://microsoftedge.github.io/Demos/demo-to-do/');

  // Add a new todo item using the label '➕ Add a task'
  await page.getByLabel('➕ Add a task').fill('Buy groceries');
  await page.click('input[value="➡️"]');

  // Verify the new todo item is added
  var todoItems = page.locator('#tasks li .text');
  await expect(todoItems).toHaveCount(1);
  await expect(todoItems.nth(0)).toHaveText('Buy groceries');

  // Add another todo item
  await page.getByLabel('➕ Add a task').fill('Walk the dog');
  await page.click('input[value="➡️"]');

  // Update the locator for todo items


  // Verify both todo items are present
  await expect(todoItems).toHaveCount(2);
  await expect(todoItems.nth(0)).toHaveText('Walk the dog');
  await expect(todoItems.nth(1)).toHaveText('Buy groceries');
  

  // Mark the first todo item as completed
  await todoItems.nth(0).locator('.box').check();

  // Verify the first todo item is marked as completed
  await expect(todoItems.nth(0)).toHaveClass(/completed/);

  // Delete the second todo item
  await todoItems.nth(1).hover();
  await todoItems.nth(1).locator('.destroy').click();

  // Verify the second todo item is deleted
  await expect(todoItems).toHaveCount(1);
});