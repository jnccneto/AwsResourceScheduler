/**
 * @name Amazon product search
 * @desc Searches Amazon.com for a product and checks if the results show up
 */

const puppeteer = require('puppeteer')
let browser
let page
jest.setTimeout(50000);


beforeAll(async () => {
  browser = await puppeteer.launch({headless: true})
  page = await browser.newPage()
})

describe('DashBoard Login Test', () => {
  test('Login', async () => {  
  console.log('process.env.DASHBOARD_URL: ' + process.env.DASHBOARD_URL)	
  console.log('process.env.DASHBOARD_USER: ' + process.env.DASHBOARD_USER)
  console.log('process.env.DASHBOARD_PWD: ' + process.env.DASHBOARD_PWD)

  await page.setViewport({ width: 1920, height: 1080 }); 
  await page.goto(process.env.DASHBOARD_URL)

	const input = await page.$('#username');
	await input.click({ clickCount: 3 })
	await input.type(process.env.DASHBOARD_USER);
  await page.type('#password', process.env.DASHBOARD_PWD)
  await page.click('[type="Submit"]')
    
  await page.waitForSelector('#TestOK')
	let element = await page.$('#TestOK')
	let value = await page.evaluate(el => el.textContent, element)
	console.log('value: ' + value)
  
  expect(element).toBeTruthy()
  })
  
  afterAll(async () => {
    await browser.close()
  })  
})
