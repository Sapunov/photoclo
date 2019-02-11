<template>
    <img id="imageItem" v-bind:src="'http://photoclo.ru:8000' + imageURL" alt=""/>
</template>

<script>
    
	export default {
		name: 'imageItem',
		props: ['imageURL'],
		methods: {}
	}
</script>

<style scoped>
    #imageItem {
    	border: 0px solid black;
        margin: 5px;
        margin-top: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
    }

    #imageItem:hover {
    	opacity: 0.8;
    	cursor: pointer;
    }
</style>