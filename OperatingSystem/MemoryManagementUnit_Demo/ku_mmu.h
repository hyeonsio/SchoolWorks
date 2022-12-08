#pragma once
#include <stdio.h>
#include <stdlib.h>

char* ku_mmu_mem;
char* ku_mmu_swap;

typedef struct ku_pte {
	unsigned char value;
}ku_pte;

// mmu_node handled in queue
typedef struct ku_mmu_node {
	unsigned char offset; // physical memory/swap space offset. starts from 0 and unchange
	ku_pte* pte;
	struct ku_mmu_node* next;
}ku_mmu_node;

// mmu_PCB handled in Stack
typedef struct ku_mmu_PCB {
	unsigned char pid;
	ku_pte* page_table;
	struct ku_mmu_PCB* next;
}ku_mmu_PCB;

typedef struct ku_mmu_Queue{
	ku_mmu_node* head;
	ku_mmu_node* tail;
}ku_mmu_Queue;

typedef struct ku_mmu_Stack {
	ku_mmu_PCB* top;
}ku_mmu_Stack;

// use Queue since Swapping is in FIFO
ku_mmu_Queue ku_mmu_mem_free;  // physical addr, free space, pte == NULL
ku_mmu_Queue ku_mmu_mem_alloc; // physical addr, alloc space, pte != NULL
ku_mmu_Queue ku_mmu_swap_free;  // swapping space, free space, pte == NULL
ku_mmu_Queue ku_mmu_swap_alloc; // swapping space, alloc space, pte != NULL

// use Stack since there's no killing process, just adding
ku_mmu_Stack ku_mmu_PCBs;

// initialize mmu_node, pte = NULL
void ku_mmu_initNode(ku_mmu_node** n_node, unsigned char offset);

//insert and delete from the queues
void ku_mmu_insert(ku_mmu_Queue* queue, ku_mmu_node* n_node);
ku_mmu_node* ku_mmu_delete(ku_mmu_Queue* queue);

//initialize PCB and push to PCBs
ku_mmu_PCB* ku_mmu_push(unsigned char pid);

//get pcb from Stack, if there is no PCB, return NULL
ku_mmu_PCB* ku_mmu_get_PCB(unsigned char pid);

// get PTE
ku_pte* ku_mmu_get_PTE(unsigned char pid, unsigned char vpn);

void* ku_mmu_init(unsigned int mem_size, unsigned int swap_size) {

	if (mem_size < 4 || swap_size < 4 || (mem_size % 4) || (swap_size % 4))	return 0;

	// space allocation of mem, swap
	ku_mmu_mem = malloc(sizeof(char) * mem_size);
	ku_mmu_swap = malloc(sizeof(char) * swap_size);

	// initialize mmu_Queues and a mmu_Stack
	ku_mmu_mem_free.head = ku_mmu_mem_free.tail = NULL;
	ku_mmu_mem_alloc.head = ku_mmu_mem_alloc.tail = NULL;
	ku_mmu_swap_free.head = ku_mmu_swap_free.tail = NULL;
	ku_mmu_swap_alloc.head = ku_mmu_swap_alloc.tail = NULL;
	ku_mmu_PCBs.top = NULL;

	// malloc pmem_nodes, initialize and put into pmem_free, mmu_pmem ~ mmu_pmem + 3 allocated for OS
	for (int i = 1; i < mem_size/4; i++) {
		ku_mmu_node* n_node = malloc(sizeof(ku_mmu_node));
		ku_mmu_initNode(&n_node, i);
		ku_mmu_insert(&ku_mmu_mem_free, n_node);
	}
	// malloc swap_nodes, initialize and put into swap_free, offset starts from 4
	for (int i = 1; i < swap_size/4; i++) {
		ku_mmu_node* n_node = malloc(sizeof(ku_mmu_node));
		ku_mmu_initNode(&n_node, i);
		ku_mmu_insert(&ku_mmu_swap_free, n_node);
	}

	return (void*)ku_mmu_mem;
}

// fail -1, success 0
int ku_run_proc(char pid, void** ku_cr3) {

	unsigned char upid = (unsigned char)pid;
	ku_mmu_PCB* block = ku_mmu_get_PCB(upid);
	
	// if there is no block add block
	if (!block) block = ku_mmu_push(upid);	        
	if(!block->page_table) return -1;

	*ku_cr3 = block->page_table;
	
	return 0;
}

//fail -1, success 0
int ku_page_fault(char pid, char va) {

	unsigned char upid = (unsigned char)pid;
	unsigned char uva = (unsigned char)va;

	//get pte using vpn
	char vpn = uva >> 2;
	ku_pte* pte = ku_mmu_get_PTE(upid, vpn);

	if (!pte) return -1;


	// if pte is allocated, pte is in swap_alloc
	if (pte->value) {
		// if swap_alloc is empty, fails
		if (!ku_mmu_swap_alloc.head) return -1;

		// find node from mmu_swap_alloc and take off, initialize and put back in swap_free
		ku_mmu_node* cur = ku_mmu_swap_alloc.head;
		ku_mmu_node* sa = NULL;

		if (cur->pte == pte) sa = ku_mmu_delete(&ku_mmu_swap_alloc);
		else {
			while (1) {
				if (!cur->next) return -1;// if there is no pte in mem_alloc, fails
				else if (cur->next->pte == pte) break;
				else cur = cur->next;
			}
			sa = cur->next;
			cur->next = sa->next;
		}

		// put sa in to mem_swap_free
		sa->pte = NULL;
		ku_mmu_insert(&ku_mmu_swap_free, sa);
	}

	// if free space exists allocate it 
	if (ku_mmu_mem_free.head) {
		// delete, insert node
		ku_mmu_node* mf = ku_mmu_delete(&ku_mmu_mem_free);
		pte->value = ((mf->offset << 2) | 1);
		mf->pte = pte;
		ku_mmu_insert(&ku_mmu_mem_alloc, mf);
	}
	// if there is free swap space, swap out and alloc
	else if (ku_mmu_swap_free.head) {

		// delete nodes.
		ku_mmu_node* ma = ku_mmu_delete(&ku_mmu_mem_alloc);
		ku_mmu_node* sf = ku_mmu_delete(&ku_mmu_swap_free);

		// swap out
		sf->pte = ma->pte;
		sf->pte->value = (sf->offset << 1);
		ku_mmu_insert(&ku_mmu_swap_alloc, sf);

		// alloc mem
		pte->value = ((ma->offset << 2) | 1);
		ma->pte = pte;
		ku_mmu_insert(&ku_mmu_mem_alloc, ma);
	}
	// else, there is no empty space for the allocation
	else return -1;

	return 0;
}

void ku_mmu_initNode(ku_mmu_node** n_node, unsigned char offset) {
	(*n_node)->offset = offset;
	(*n_node)->pte = NULL;
	(*n_node)->next = NULL;
}

void ku_mmu_insert(ku_mmu_Queue* queue, ku_mmu_node* n_node) {
	if (queue->head == NULL) queue->head = queue->tail = n_node;
	else queue->tail = queue->tail->next = n_node;
}

ku_mmu_node* ku_mmu_delete(ku_mmu_Queue* queue) {

	if (!queue->head) return NULL;
	else {
		ku_mmu_node* rt = queue->head;
		queue->head = queue->head->next;
		rt->next = NULL;
		return rt;
	}
}

ku_mmu_PCB* ku_mmu_push(unsigned char pid) {

	ku_mmu_PCB* block = malloc(sizeof(ku_mmu_PCB));
	block->pid = pid;

	// page_table initially neither mapped nor swapped out
	block->page_table = calloc(64, sizeof(ku_pte));

	if (ku_mmu_PCBs.top == NULL) {
		block->next = NULL;
		ku_mmu_PCBs.top = block;
	}
	else {
		block->next = ku_mmu_PCBs.top;
		ku_mmu_PCBs.top = block;
	}

	return block;
}

//get pcb from Stack, if there is no PCB, return NULL
ku_mmu_PCB* ku_mmu_get_PCB(unsigned char pid) {
	ku_mmu_PCB* cur = ku_mmu_PCBs.top;
	while (cur) {
		if (cur->pid == pid) break;
		cur = cur->next;
	}
	return cur;
}

// get PTE
ku_pte* ku_mmu_get_PTE(unsigned char pid, unsigned char vpn) {

	// get PCB whose pid == pid
	ku_mmu_PCB* cur = ku_mmu_get_PCB(pid);

	// if there's no PCB return NULL
	if (!cur) return NULL;
	return &(cur->page_table[vpn]);
}
