import asyncio
from datetime import datetime as dt
from random import choice
from typing import Any

from aiohttp import ClientSession
from playwright._impl._browser import Browser
from playwright._impl._page import Page
from playwright.async_api._context_manager import PlaywrightContextManager

from config import (BROWSER_ARGS, CONSOLE_COLORS, ERROR_LIMIT, HEADLESS,
                    PAGE_LIMIT, PROXY_SITE, USER_AGENTS, WAIT_AFTER_CART,
                    WAIT_AFTER_FINISH, WEBSITE)
from scrapper.datacls import Response, Task
from scrapper.log import WildberriesLogger
from scrapper.xpath_conf import (ITEM_MAIN_PAGE, NEXT_PAGE, OPTIONS, PAGE_HEIGHT,
                        SEARCH_BLOCK)


class Chrome(PlaywrightContextManager):
    
    def __init__(self, task: Task) -> None:
        self.logger = WildberriesLogger(task._id)
        self.task = task
        self.skip_carts = task.skip_carts
        self.cycles = task.cycles
        self.color = choice(CONSOLE_COLORS)
        self.error_limit = ERROR_LIMIT
        self.browser_args = BROWSER_ARGS
        self.page_limit = PAGE_LIMIT
        self.success = False
        return super().__init__()
        
    async def __aenter__(self):
        self.manager = await super().__aenter__()
        self.proxies = await self.get_proxies()
        self.browser: Browser = None
        self.page: Page = None
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        return await super().__aexit__(*args)
    
    async def get_proxies(self):
        async with ClientSession() as session:
            async with session.get(PROXY_SITE) as r:
                json = await r.json()
                response = Response.parse_obj(json)
                return list(response.list.values())

    async def launch(self):
        proxy = choice(self.proxies)
        self.browser_args.append(
            f'--user-agent={choice(USER_AGENTS)}',
        )
        await self.logger.log(
            f'Подключение через прокси: {proxy.ip}:{proxy.port}'
        )
        
        self.browser = await self.manager.chromium.launch(
            proxy={
                "server": f'http://{proxy.ip}:{proxy.port}',
                "username": proxy.login,
                "password": proxy.password
            },
            args=self.browser_args,
            headless=HEADLESS
        )

    async def close(self):
        await self.browser.close()
   
    async def load_page(self):
        self.success = False
        self.page = await self.browser.new_page()
        await self.page.goto(WEBSITE)
        self.page.set_default_timeout(3000)
        await self.logger.log('Сайт: ОК')
        
    async def perform_search(self):
        try:
            search_box = self.page.locator(f"xpath={SEARCH_BLOCK}")
            await self.wait(2)
            await search_box.click()
            await self.wait(2)
            await search_box.type(self.task.prompt, delay=200, timeout=20000)
            await self.wait(2)
            await search_box.press('Enter')
            self.page.get_by_text('По запросу')
            await self.wait(2)
            await self.logger.log('Поиск: ОК')
            return True
        except Exception as ex:
            await self.logger.log(
                f'Поиск: Ошибка - {type(ex).__name__}'
            )
            await self.browser.close()
            return False

    async def wait(self, seconds: int):
        await asyncio.sleep(seconds)
    
    async def smooth_scroll(self, height):
        for i in range(1, height, 5):
            await self.page.evaluate(f'window.scrollTo(0, {i});')
        await self.wait(2)
    
    async def next_page(self):
        try:
            
            next_page = self.page.locator(f'css={NEXT_PAGE}')
            await next_page.hover()
            await asyncio.sleep(2)
            await next_page.click()
            await self.logger.log(
                'Переход на следующую страницу'
            )
            return True
        except Exception as ex:
            await self.logger.log(
                'Последняя страница'
            )
            return False
    
    async def locate_item(self):
        for page_num in range(1, self.page_limit):
            try:
                await self.logger.log(
                    f'Страница {page_num}'
                )
                await self.smooth_scroll(PAGE_HEIGHT)
                item = self.page.locator(f'#c{self.task.item_id}')
                await item.hover(timeout=5000)
                await self.wait(2)
                await item.click()
                await self.wait(2)
                await self.logger.log(
                    'Товар: ОК'
                )
                return True
            except Exception as ex:
                if not await self.next_page():
                    await self.browser.close()
                    await self.logger.log(
                        f'Перезапуск цикла, осталось циклов: {self.task.cycles}'
                    )
                    return False
        
    async def add_to_cart(self, primary=True):
        await self.wait(2)
        try:
            cart = self.page.get_by_role(
                'button',
                name='Добавить в корзину'
            )
            await cart.click()
            await self.wait(WAIT_AFTER_CART)
            await self.logger.log(
                'Корзина: ОК'
            )
            if primary:
                self.success = True
        except Exception as ex:
            await self.logger.log(
                f'Корзина: Ошибка - {type(ex).__name__}'
            )
            await self.wait(1)

    async def select_item_options(self):
        await self.wait(5)
        try:
            option = self.page.locator(OPTIONS).first
            await option.click()
            await self.wait(2)
        except Exception:
            pass
    
    async def skip_cart(self):
        self.task.skip_carts -= 1
        self.success = True
    
    async def refresh_skip_carts(self):
        self.skip_carts = self.task.skip_carts
    
    async def count_error(self):
        self.error_limit -= 1
    
    async def return_to_first_page(self):
        await self.logger.log(
            'Возврат на первую страницу'
        )
        try:
            first_page = self.page.locator(
                'a.pagination-item.pagination__item.j-page', has_text='1')
            await first_page.hover()
            await self.wait(2)
            await first_page.click()
        except:
            pass
        return True
    
    async def click_random_item(self):
        try:
            await self.wait(5)
            attempts = 7
            while attempts:
                item = self.page.locator(
                    ITEM_MAIN_PAGE.format(choice(range(1, 6)))
                )
                if 'product-card--adv' in await item.get_attribute('class'):
                    attempts -= 1
                    continue
                await item.hover()
                await self.wait(5)
                await item.click()
                break

            await self.logger.log(
                f'Выбран товар {await item.get_attribute("data-nm-id")}'
            )
            await self.wait(10)
        except Exception as ex:
            await self.logger.log(ex)

    async def click_cart(self):
        await self.wait(5)
        try:
            cart = self.page.get_by_text('Корзина')
            await cart.hover()
            await self.wait(2)
            await cart.click()
            await self.page.wait_for_load_state()
            await self.wait(10)
            await self.logger.log(
                'Переход в корзину'
            )
        except Exception as ex:
            await self.logger.log(ex)

    async def get_time(self):
        return self.color + dt.now().strftime("%H:%M:%S")

async def script(task: Task):
    async with Chrome(task) as chrome:
        while task.cycles and chrome.error_limit:
            try:
                await chrome.launch()
            except Exception as ex:
                await chrome.logger.log(ex)
                await chrome.count_error()
                continue
            try:
                await chrome.load_page()
            except Exception as ex:
                await chrome.logger.log(ex)
                await chrome.close()
                continue
            try:
                await chrome.perform_search()
            except Exception as ex:
                await chrome.logger.log(ex)
                await chrome.close()
                continue
            if not await chrome.locate_item():
                await chrome.count_error()
                await chrome.close()
                continue
            if not task.skip_carts:
                await chrome.select_item_options()
                await chrome.add_to_cart()
                await chrome.refresh_skip_carts()
                await chrome.page.go_back()
                await chrome.return_to_first_page()
                await chrome.smooth_scroll(3000)
                await chrome.click_random_item()
                await chrome.select_item_options()
                await chrome.add_to_cart(primary=False)
                await chrome.refresh_skip_carts()
            else:
                await chrome.click_cart()
                await chrome.skip_cart()
            if not chrome.success:
                await chrome.logger.log(
                    f'Перезапуск цикла, осталось циклов: {task.cycles}'
                )
                await chrome.close()
                await chrome.count_error()
                continue
            else:
                task.cycles -= 1
                await chrome.logger.log(
                    f'Цикл завершён, осталось циклов: {task.cycles}'
                )
                await chrome.close()
            await chrome.wait(WAIT_AFTER_FINISH)        
        if not chrome.error_limit:
            await chrome.logger.log(
                f'Достигнут лимит ошибок по задаче'
            )
            return False
        await chrome.logger.log(
            'Задача завершена'
        )
        return True

