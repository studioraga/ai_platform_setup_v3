import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import App from './App'

afterEach(() => {
  cleanup()
})

describe('Vite 8 React starter contract', () => {
  it('renders the current accessible heading', () => {
    render(<App />)
    expect(screen.getByRole('heading', { level: 1, name: 'Get started' })).toBeTruthy()
  })

  it('increments the counter on click', () => {
    render(<App />)
    const counter = screen.getByRole('button', { name: 'Count is 0' })
    fireEvent.click(counter)
    expect(screen.getByRole('button', { name: 'Count is 1' })).toBeTruthy()
  })

  it('starts with a clean render in every test', () => {
    render(<App />)
    expect(screen.getAllByRole('button', { name: 'Count is 0' })).toHaveLength(1)
  })
})
