/**
 * @name dashboard Login
 *
 * @desc Provide your username and password as environment variables when running the script, i.e:
 * DASBOARD_USER DASBOARD_PWD DASHBOARD_URL
 *
 */
const puppeteer = require('puppeteer')
const screenshot = 'dashboard.png';
(async () => {
	
  console.log('process.env.DASHBOARD_URL: ' + process.env.DASHBOARD_URL)	
  console.log('process.env.DASHBOARD_USER: ' + process.env.DASHBOARD_USER)
  console.log('process.env.DASHBOARD_PWD: ' + process.env.DASHBOARD_PWD)

  const browser = await puppeteer.launch({headless: false})
  const page = await browser.newPage()
  await page.setViewport({ width: 1920, height: 1080 }); 
  await page.goto(process.env.DASHBOARD_URL)


	const input = await page.$('#username');
	await input.click({ clickCount: 3 })
	await input.type(process.env.DASHBOARD_USER);
  await page.type('#password', process.env.DASHBOARD_PWD)
 
  
  await Promise.all([
     page.click('[type="Submit"]'),
     //page.waitForNavigation({waitUntil: 'networkidle0',timeout: 5000})
  ]);


 
  await page.waitForSelector('#TestOK')
	let element = await page.$('#TestOK')
	let value = await page.evaluate(el => el.textContent, element)
	console.log('value: ' + value)
  await page.screenshot({ path: screenshot })
  browser.close()
  console.log('Script Ended: ')
})()



async function open_tab(setting) {
  try {
   
  console.log('process.env.DASHBOARD_URL: ' + process.env.DASHBOARD_URL)	
  console.log('process.env.DASHBOARD_USER: ' + process.env.DASHBOARD_USER)
  console.log('process.env.DASHBOARD_PWD: ' + process.env.DASHBOARD_PWD)

  const browser = await puppeteer.launch({headless: false})
  const page = await browser.newPage()
  await page.setViewport({ width: 1920, height: 1080 }); 
  await page.goto(process.env.DASHBOARD_URL)


	const input = await page.$('#username');
	await input.click({ clickCount: 3 })
	await input.type(process.env.DASHBOARD_USER);

  //await page.type('#username', process.env.DASHBOARD_USER)
  await page.type('#password', process.env.DASHBOARD_PWD)
  await page.click('[type="Submit"]')
  
    await Promise.all(page.$eval('form', form => form.submit()), page.waitForNavigation());
    console.log(' -> don!  ');
    await page.close();
  } catch (error) {
    console.log(' -> somethign went wrong !', error);
    await page.close();
  }
}
